# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
"""BikaSQLStorage writes field values to AttributeStorage and also
queues writes to PostgreSQL connection.
"""
import os
import random
from copy import copy
from os.path import exists

import psycopg2
from Products.ATExtensions.field import RecordField
from Products.ATExtensions.field import RecordsField
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Storage import AttributeStorage
from Products.Archetypes.interfaces import IObjectField
from Products.Archetypes.utils import setSecurity
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from ZPublisher.pubevents import PubSuccess
from persistent.list import PersistentList
from plone.api.portal import get
# noinspection PyUnresolvedReferences
from psycopg2 import ProgrammingError
# noinspection PyUnresolvedReferences
from psycopg2.extensions import connection

marker = random.random()

# The name of the attribute on the portal root which will contain
# the queue of queries to be executed against the sql server.
SQL_QUEUE = 'bika_sql_query_queue'

IGNORE_FIELDNAMES = [
    'allowDiscussion', 'subject', 'location', 'contributors', 'creators',
    'effectiveDate', 'expirationDate', 'language', 'rights']


class BikaSQLStorage(AttributeStorage):
    """Support writing field values to SQL tables.
    """

    def __init__(self):
        pass

    def set(self, name, instance, value, **kwargs):
        """Set the value in AttributeStorage and queue it to be written out to
        sql database.

        :param name: Field name in the AT schema.
        :type name: string
        :param instance: The object being edited
        :type instance: BaseContent
        :param value: The field value
        :type value: Any
        :param kwargs: Passed directly to base class' set().
        :type kwargs: dict
        :return: None 
        :rtype: NoneType
        """
        uid = instance.UID()
        # Ignore objects under creation
        if not hasattr(instance, 'aq_parent'):
            return
        # Write field to AttributeStorage
        AttributeStorage.set(self, name, instance, value, **kwargs)
        # Write values to request
        name.lower()
        if name not in IGNORE_FIELDNAMES:
            request_queue = instance.REQUEST.get('_sql_queue', {})
            # Here, the default value, has the UID stuck into it.
            this = request_queue.get(uid, {'UID': instance.UID()})
            this[name] = value
            request_queue[uid] = this
            instance.REQUEST.set('_sql_queue', request_queue)

    def unset(self, name, instance, **kwargs):
        """Explicitly set the field value to an empty value.

        :param name: Field name in the AT schema.
        :type name: string
        :param instance: The object being edited
        :type instance: BaseContent 
        :param kwargs: Passed directly to base class' unset().
        :type kwargs: dict
        :return: a thing
        :rtype: NoneType
        """
        uid = instance.UID()
        # Ignore objects under creation
        if not hasattr(instance, 'aq_parent'):
            return
        # Write field to AttributeStorage
        AttributeStorage.unset(self, name, instance, **kwargs)
        # Write empty/deleted value to request
        if name not in IGNORE_FIELDNAMES:
            request_queue = instance.REQUEST.get('_sql_queue', {})
            this = request_queue.get(uid, {'UID': instance.UID()})
            this[name] = ''
            request_queue[uid] = this
            instance.REQUEST.set('_sql_queue', request_queue)


setSecurity(BikaSQLStorage)


def RequestQueueToSQLQueue(event):
    """BikaSQLStorage combines write events into a dictionary, keyed by object
    UID, and writes them to the request.  This combines writes on an object
    during one request into a single item.
    
    At the end of each request, this function writes these dictionaries into
    the list at portal.SQL_QUEUE.
    
    :param event: Success event IPubSucess
    :type event: PubSuccess
    """
    r_queue = event.request.get('_sql_queue', {})
    if r_queue:
        portal = get()
        # get queue
        if SQL_QUEUE not in dir(portal):
            setattr(portal, SQL_QUEUE, PersistentList())
        queue = getattr(portal, SQL_QUEUE)
        # Write value to queue
        queue.extend(r_queue.values())


class SQLQueueRunner(BrowserView):
    """This runner requires modification of the buildout.
    Example configuration (in buildout.cfg):

        [buildout]
        environment-vars +=
            PGSQL_DSN user=testuser password=testpass dbname=testdb
        
        parts =
            <existing parts>
            sql_queue_runner

        [sql_queue_runner]
        <= client_base
        recipe = plone.recipe.zope2instance
        zeo-address = ${zeoserver:zeo-address}
        http-address = <unused port number>
        zope-conf-additional =
            <clock-server>
               method /Plone/sql_queue_runner
               period 10
               user admin
               password adminsecret
               host localhost
            </clock-server>

    The script can then be invoked with `bin/sql_queue_runner start`,
    like any other zeo client.
    
    For more information on the format of the DSN, visit the psycopg2 docs.
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.conn = None
        self.cur = None

    def __call__(self):
        """Write entire contents of sql queue to the relational database,
        clear the queue and exit.

        If another instance of the clock is running, this one will silently die.

types of fields to convert

    blob field eg 'AccreditationBodyLogo': <plone.app.blob.field.BlobWrapper
    dict eg all RecordFields
    list of dict, eg all RecordsFields
    
        """
        if self.is_locked():
            return
        self.lock()
        try:
            # Create a new connection and cursor
            self.connect()

            queue = [copy(x) for x in self.get_queue()]
            print("queue is {} long".format(len(queue)))

            uc = getToolByName(self.context, 'uid_catalog')
            for values in queue:
                # Get the instance object
                uid = values['UID']
                instance = uc(UID=uid)[0].getObject()
                # Generate queries and execute
                queries = SQLQuery(instance, self.conn, values)
                queries()
                # clear contents of queue
                self.reset_queue()
        finally:
            self.unlock()

    def lock(self):
        """Acquire lock

        :return: None
        :rtype: NoneType
        """
        open('/tmp/XXX_pdb', 'w').write('go away')

    def unlock(self):
        """Unlock, permits new clock instances to proceed.

        :return: None
        :rtype: NoneType
        """
        try:
            os.unlink('/tmp/XXX_pdb')
        except OSError:
            pass

    def is_locked(self):
        """Check lock status
        
        :return: True if another sql runner is busy here.
        :rtype: bool
        """
        if exists('/tmp/XXX_pdb'):
            return True
        return False

    def connect(self):
        """Create connection to database.
        Set instance variables:

        - self.conn = connection
        """
        self.conn = psycopg2.connect(os.environ.get('PGSQL_DSN'))

    def get_queue(self):
        """Retrieve the SQL_QUEUE object from the portal root. 

        :return: A list of queries to be performed.
        :rtype: PersistentList
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        if SQL_QUEUE not in dir(portal):
            setattr(portal, SQL_QUEUE, PersistentList())
        return getattr(portal, SQL_QUEUE)

    def reset_queue(self):
        """Empty the queue once it's been written out.
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        setattr(portal, SQL_QUEUE, PersistentList())


class SQLQuery:
    """Create SQL queries from a dictionary, and execute them.
    """

    type_map = {
        'string': 'TEXT',
        'datetime': 'TIMESTAMP',
        'fixedpoint': 'NUMERIC',
        'lines': 'TEXT',
        'reference': 'TEXT',
        'uidreference': 'TEXT',
        'object': 'TEXT',
        'float': 'NUMERIC',
    }

    def __init__(self, instance, conn, values):
        """
        :param instance: The object to be edited or created.
        :type instance: BaseContent
        :param conn: DB connection from psycopg
        :type conn: connection
        :param values: One dictionary from SQL_QUEUE.  Contains UID key,
        other keys are fieldname:value pairs.
        :type values: dict
        """
        self.instance = instance
        self.conn = conn
        self.values = values

        # A list of SQL query strings will go here:
        self.queries = []

        self.create_tables()
        self.compose_queries()

    def __call__(self):
        cur = self.conn.cursor()
        for query in self.queries:
            cur.execute(query)
        self.conn.commit()

    def create_tables(self):
        """CREATE TABLE queries are queued if the primary portal_type table
        does not exist.  Supplementary tables are created for some fields:

        - Dictionary or List of Dictionary (RecordField, RecordsField):
          create a table with column f\or each key of dictionary.

        - Other list or tuple (LinesField, multiValued reference):
          create table containing only UID and value columns
          
        If a table for a specific portal_type does not exist, this function
        will trigger a walker which will import values for every existing
        object of the same type.
        """

        instance = self.instance
        uid = instance.UID()
        tablename = instance.portal_type.lower()

        # Main portal_type table exists already?
        cur = self.conn.cursor()
        try:
            q = 'select * from {} where uid="{}"'.format(tablename, uid)
            cur.execute(q)
            return
        except ProgrammingError:
            pass
        finally:
            self.conn.rollback()

        # divide all schema fields into categories
        fields, dict_fields, list_fields = self.get_fields()

        # Create main portal_type table.
        columns = []
        for field in fields:
            colname = self._colname(field)
            coltype = self._coltype(field)
            columns.append('{} {}'.format(colname, coltype))
        columns = ','.join(columns)
        self.queries.append(
            "CREATE TABLE IF NOT EXISTS {} ("
            "UID TEXT PRIMARY KEY NOT NULL, "
            "PARENTUID TEXT, {});".format(tablename, columns))

        # Create lookup tables for dict values
        # I will use TEXT for all columns.
        for field in dict_fields:
            fieldname = field.getName()
            tablename = "{}_{}".format(instance.portal_type.lower(), fieldname)
            subfields = field.subfields
            columns = ','.join(['{} TEXT'.format(f) for f in subfields])
            self.queries.append(
                "CREATE TABLE IF NOT EXISTS {} ("
                "{}_UID TEXT PRIMARY KEY NOT NULL, "
                "{});".format(tablename, instance.portal_type.lower(), columns))

        # Create lookup tables for list-containing and multiValued fields
        # I will use TEXT for the value column.
        for field in list_fields:
            fieldname = field.getName()
            tablename = "{}_{}".format(instance.portal_type.lower(), fieldname)
            self.queries.append(
                "CREATE TABLE IF NOT EXISTS {} "
                "({}_UID TEXT PRIMARY KEY NOT NULL, value TEXT);".format(
                    tablename, instance.portal_type.lower()))

    def compose_queries(self):
        """Generate a set of SQL queries required to insert or update
        the fieldnames and values specified in self.values
        
        :return: List of query strings.
        :rtype: list
        """
        uid = self.instance.UID()
        p_uid = self.instance.aq_parent.UID()
        ptname = self.instance.portal_type.lower()
        tablename = ptname

        # divide used fields (those in self.values) into categories
        fields, dict_fields, list_fields = self.get_fields(values_only=True)

        import pdb;
        pdb.set_trace();
        pass

        # Query to insert/update values into the main portal_type table
        if self.exists_in_table(tablename, 'UID', uid):
            z = ['{}={}'.format(self._colname(f), self._colval(f))
                 for f in fields]
            query = "UPDATE {} SET {} WHERE UID='{}'".format(
                tablename, ','.join(z), uid)
        else:
            colnames = ['UID', 'PARENTUID'] + \
                       [self._colname(f) for f in fields]
            colvals = ["'%s'" % uid, "'%s'" % p_uid] + \
                      [self._colval(f) for f in fields]
            query = "INSERT INTO {} ({}) VALUES ({})".format(
                tablename, ','.join(colnames), ','.join(colvals))
        self.queries.append(query)

        # Dict field types, insert or update lookup value table
        for field in dict_fields:
            fieldname = field.getName()
            tablename = "{}_{}".format(ptname, fieldname)
            val = self.values[fieldname]
            colnames = field.subfields
            colvals = ["'{}'".format(val[colname]) for colname in colnames]
            if self.exists_in_table(tablename, '{}_UID'.format(ptname), uid):
                z = ['{}={}'.format(*x) for x in zip(colnames, colvals)]
                query = "UPDATE {} SET {} WHERE {}_UID='{}'".format(
                    tablename, ','.join(z), ptname, uid)
            else:
                query = "INSERT INTO {} ({}_UID, {}) VALUES ('{}', {})".format(
                    tablename, ptname, ','.join(colnames), uid,
                    ','.join(colvals))
            self.queries.append(query)

        # List field types, insert or update lookup value table
        for field in list_fields:
            fieldname = field.getName()
            tablename = "{}_{}".format(ptname, fieldname)
            if self.exists_in_table(tablename, '{}_UID'.format(ptname), uid):
                query = 'UPDATE {} SET value={} WHERE {}_UID="{}"'.format(
                    tablename, val, ptname, uid)
            else:
                query = 'INSERT INTO {} (value, {}_UID) VALUES ({}, {})'.format(
                    tablename, ptname, val, uid)
            self.queries.append(query)

    def exists_in_table(self, tablename, col, uid):

        """Return true if the instance already has a record in the DB.
        A CREATE TABLE query is queued if the table does not exist
        
        :param tablename: The name of the table we're searching in
        :type tablename: string
        :param col: The column to check for the value's existence.
        :type col: string
        :param uid: The UID of the row we're checking for
        :type uid: string
        """

        cur = self.conn.cursor()
        # noinspection PyBroadException
        try:
            query = "select * from {} where {}='{}'".format(tablename, col, uid)
            cur.execute(query)
            cur.fetchone()
        except:
            return False
        finally:
            self.conn.rollback()
        return True

    def get_fields(self, values_only=False):

        """Get only fields from instance schema that use the BikaSQLStorage.
        
        :param values_only: Only return fields which exist in self.values
        :type values_only: bool
        :return: A list of schema field objects
        :rtype: list
        """

        dict_fields = []
        list_fields = []
        fields = []  # single-valued fields

        allfields = []
        schema = self.instance.Schema()
        for field in schema.fields():
            if IObjectField.providedBy(field) \
                    and field.getStorage() == BikaSQLStorage():
                if values_only and field.getName() not in self.values:
                    continue
                allfields.append(field)

        # Find fields that need their own lookup tables
        # and don't include them in the 'fields' list
        for f in allfields:
            if isinstance(f, RecordField) or isinstance(f, RecordsField):
                dict_fields.append(f)
            elif f.multiValued:
                list_fields.append(f)
            else:
                fields.append(f)

        return fields, dict_fields, list_fields

    def _colname(self, field):
        """Return a valid column name.

        :param field: A schema field who's name will be used.
        :type field: ObjectField
        """
        fieldname = field.getName()
        return fieldname

    def _coltype(self, field):
        """Return a column type which will store values from this field.

        :param field: A schema field who's type will be used.
        :type field: ObjectField
        """
        fieldtype = field.type
        nt = self.type_map.get(fieldtype, 'TEXT')
        print "type of {} ({}): {}".format(field, fieldtype, nt)
        return nt

    def _colval(self, field):
        """Return the field value, munged and quoted to fit the column.

        :param field: A schema field who's value we want to return.
        :type field: ObjectField
        """
        fieldname = field.getName()
        unquoted_types = ['NUMERIC', 'INTEGER']

        val = self.values[fieldname]
        mutator = getattr(self, 'mutate_{}'.format(field.type), None)
        if mutator:
            val = mutator(val)

        return val if self._coltype(field) in unquoted_types else "'%s'" % val

    def mutate_lines(self, val):
        return '\n'.join(val)

    def mutate_datetime(self, val):
        if val:
            return val.ISO()
