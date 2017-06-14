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
# noinspection PyUnresolvedReferences
from psycopg2 import ProgrammingError

import psycopg2
from DateTime import DateTime
from Products.ATExtensions.field import RecordField
from Products.ATExtensions.field import RecordsField
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Storage import AttributeStorage
from Products.Archetypes.interfaces import IObjectField
from Products.Archetypes.utils import setSecurity
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from ZPublisher.pubevents import PubSuccess
from bika.lims import logger
from persistent.list import PersistentList
from plone.api.portal import get
# noinspection PyUnresolvedReferences
from plone.app.blob.field import BlobWrapper

marker = random.random()

# The name of the attribute on the portal root which will contain
# the queue of queries to be executed against the sql server.
SQL_QUEUE = 'bika_sqlstorage_queue'

class BikaSQLQueue(PersistentList):
    """This is just PersistentList, but I stubbed it here for debugging.
    I've left the stub active because one never knows what the future holds.
    """
    def __setitem__(self, i, item):
        import pdb;pdb.set_trace();pass
        self.__super_setitem(i, item)
        self._p_changed = 1


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
        request_queue = instance.REQUEST.get('_sql_queue', {})
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
        request_queue = instance.REQUEST.get('_sql_queue', {})
        this = request_queue.get(uid, {'UID': instance.UID()})
        this[name] = ''
        request_queue[uid] = this
        instance.REQUEST.set('_sql_queue', request_queue)


setSecurity(BikaSQLStorage)


def RequestQueueToSQLQueue(event):
    """BikaSQLStorage combines write events into a dictionary, keyed by object
    UID, and writes them to the request.  This combines writes on an object
    during one request into a single item. At the end of each request, 
    this function writes these dictionaries into the list at portal.SQL_QUEUE.
    
    :param event: Success event IPubSucess
    :type event: PubSuccess
    """
    r_queue = event.request.get('_sql_queue', {})
    if r_queue:
        portal = get()
        # get queue
        if SQL_QUEUE not in dir(portal):
            setattr(portal, SQL_QUEUE, BikaSQLQueue())
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

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request
        self.conn = None

    def __call__(self):
        """Write entire contents of sql queue to the relational database,
        clear the queue and exit.

        If another instance of the clock is running, this one will silently die.
        
        If the database is not initialised, this will cause all tables to 
        be created, and existing field values to be imported.
        """
        # Force this code to access ZODB as 'admin' user.
        app = self.context.aq_parent
        from AccessControl.SecurityManagement import newSecurityManager
        user = app.acl_users.getUser('admin')
        newSecurityManager(None, user.__of__(app.acl_users))

        # noinspection PyUnresolvedReferences
        self.conn = psycopg2.connect(os.environ.get('PGSQL_DSN'))

        try:
            if not self.is_locked():
                self.run_queue()
        except ProgrammingError:
            # First run? initialize db.
            self.initialize()

    def initialize(self):
        """Create tables for all discoverable portal_types who's schemas
        contain fields that support BikaSQLStorage.
        """

        self.create_lock()
        self.lock()

        try:
            # Store portal_types here, if new tables were created.  Later,
            # these portal_types will have all existing objects imported.
            created = []
            queries = []
            pt = getToolByName(self.context, 'portal_types')
            uc = getToolByName(self.context, 'uid_catalog')
            for portal_type in pt.listContentTypes():
                # XXX Bad migration, left some brains for removed types in uc:
                if portal_type in ('ARPriority', 'ARPriorities'):
                    continue
                # Try get a single instance of each portal_type to work with
                brains = uc(portal_type=portal_type)
                if not brains:
                    # If there are no instances, we will not initialize this
                    # table.  it will be created when some objects are created
                    # in the zodb.
                    continue
                instance = brains[0].getObject()
                schema = instance.Schema()
                # Has BikaSQLStorage fields?
                fields = [x for x in schema.fields()
                          if hasattr(x, 'getStorage')  # ComputedField
                          and x.getStorage() == BikaSQLStorage()]
                if fields:
                    created.append(portal_type)
                    queries.extend(
                        self.create_tables_for_type(
                            portal_type, schema))

            cur = self.conn.cursor()
            for query in queries:
                logger.info(query)
                cur.execute(query)
            self.conn.commit()

            # Import existing data for all new portal_type tables created
            for portal_type in created:
                self.import_all(portal_type)
        finally:
            self.unlock()

    def run_queue(self):
        """Generate and execute queries for all entries in SQL_QUEUE.

        :return: None
        :rtype: NoneType
        """
        # Grab the lock
        if self.is_locked():
            return
        self.lock()

        # Run the queue
        try:
            queue = [copy(x) for x in self.get_queue()]
            for values in queue:
                # Generate queries
                queries = self.compose_queries(values)
                # Execute queries
                cur = self.conn.cursor()
                for query in queries:
                    logger.info(query)
                    cur.execute(query)
                self.conn.commit()
                # clear contents of queue
                self.reset_queue()
        finally:
            self.unlock()

    def create_lock(self):
        """Create the lock table
        """
        cur = self.conn.cursor()
        query = "CREATE TABLE lock (pid TEXT, time TIMESTAMP)"
        cur.execute(query)
        self.conn.commit()

    def lock(self):
        """Acquire lock

        :return: None
        :rtype: NoneType
        """
        pid = os.getpid()
        query = "insert into lock (pid, time) values ({}, now())".format(pid)
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()

    def unlock(self):
        """Unlock, permits new clock instances to proceed.

        :return: None
        :rtype: NoneType
        """
        query = "delete from lock"
        self.conn.rollback()
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()

    def is_locked(self):
        """Check lock status
        
        :return: False if lock is not held, or PID of process holding lock.
        :rtype: bool | string
        """
        cur = self.conn.cursor()
        try:
            query = 'select * from lock'
            cur.execute(query)
            # noinspection PyStatementEffect
            cur.fetchone()[0]
        except TypeError:
            return False
        finally:
            self.conn.rollback()
        return True

    def get_queue(self):
        """Retrieve the SQL_QUEUE object from the portal root. 

        :return: A list of queries to be performed.
        :rtype: PersistentList
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        if SQL_QUEUE not in dir(portal):
            setattr(portal, SQL_QUEUE, BikaSQLQueue())
        return getattr(portal, SQL_QUEUE)

    def reset_queue(self):
        """Empty the queue once it's been written out.
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        setattr(portal, SQL_QUEUE, BikaSQLQueue())

    def create_tables_for_type(self, portal_type, schema):
        """CREATE TABLE queries are queued if the primary portal_type table
        does not exist.  Supplementary tables are created for some fields:

        - Dictionary or List of Dictionary (RecordField, RecordsField):
          create a table with column f\or each key of dictionary.

        - Other list or tuple (LinesField, multiValued reference):
          create table containing only UID and value columns
          
        If a table for a specific portal_type does not exist, this function
        will trigger a walker which will import values for every existing
        object of the same type.
        
        :param schema: AT schema containing some BikaSQLStorage fields.
        :type schema: Schema
        :param portal_type: The portal_type for which we want to create tables.
        :type portal_type: string
        :return: list of query strings
        :rtype: list
        """
        ptname = portal_type.lower()

        queries = []

        # Main portal_type table exists already?
        cur = self.conn.cursor()
        try:
            query = 'select * from {}'.format(ptname)
            cur.execute(query)
            return []
        except ProgrammingError:
            self.conn.rollback()
            pass

        # divide all schema fields into table types
        fields, dict_fields, list_fields = self.get_fields(schema)

        # Create main portal_type table.
        columns = []
        for field in fields:
            colname = field.getName()
            coltype = self._coltype(field)
            columns.append('{} {}'.format(colname, coltype))
        columns = ','.join(columns)
        queries.append(
            "CREATE TABLE IF NOT EXISTS {} ("
            "UID TEXT PRIMARY KEY NOT NULL, "
            "PARENTUID TEXT, {});".format(ptname, columns))

        # Create lookup tables for dict values
        # I will use TEXT for all columns.
        for field in dict_fields:
            fieldname = field.getName()
            tablename = "{}_{}".format(ptname, fieldname)
            subfields = field.subfields
            columns = ','.join(['{} TEXT'.format(f) for f in subfields])
            queries.append(
                "CREATE TABLE IF NOT EXISTS {} ("
                "{}_UID TEXT NOT NULL, "
                "{});".format(tablename, ptname, columns))

        # Create lookup tables for list-containing and multiValued fields
        # I will use TEXT for the value column.
        for field in list_fields:
            fieldname = field.getName()
            tablename = "{}_{}".format(ptname, fieldname)
            queries.append(
                "CREATE TABLE IF NOT EXISTS {} "
                "({}_UID TEXT NOT NULL, value TEXT);".format(
                    tablename, ptname))
        return queries

    def import_all(self, portal_type):
        """Import existing field values for objects of portal_type.

        :param portal_type: This type is searched in uid_catalog, and all found
        instances are imported.
        :type portal_type: string
        """
        uc = getToolByName(self.context, 'uid_catalog')
        brains = uc(portal_type=portal_type)
        if not brains:
            logger.info("No objects imported for {}".format(portal_type))
            return
        for brain in brains:
            instance = brain.getObject()
            # Compose dict of all BikaSQLStorage field values
            fields = [field for field in instance.Schema().fields()
                      if hasattr(field, 'getStorage')  # ComputedField
                      and field.getStorage() == BikaSQLStorage()]
            values = {f.getName(): f.getRaw(instance) for f in fields}
            values['UID'] = instance.UID()
            # Compose queries
            queries = self.compose_queries(values)
            # Execute queries
            cur = self.conn.cursor()
            for query in queries:
                logger.info(query)
                cur.execute(query)
            self.conn.commit()

    def compose_queries(self, values):
        """Generate a set of SQL queries required to insert or update
        the fieldnames and values specified in values. Values must contain 
        a UID key, referring to the object being written out.
        
        :param values: A dictionary of fieldname:value pairs.  
        :type values: dict
        :return: List of query strings.
        :rtype: list
        """
        # Get the instance object
        uc = getToolByName(self.context, 'uid_catalog')
        instance = uc(UID=values['UID'])[0].getObject()

        queries = []

        uid = instance.UID()
        parent = instance.aq_parent
        p_uid = parent.UID() if hasattr(parent, 'UID') else None
        ptname = instance.portal_type.lower()
        tablename = ptname

        # divide used fields (those in values) into table types
        fields, dict_fields, list_fields = \
            self.get_fields(instance.Schema(), values=values)

        # Query to insert/update values into the main portal_type table
        uq = "UPDATE {} SET {} WHERE UID='{}'"
        iq = "INSERT INTO {} ({}) VALUES ({})"
        if self.exists_in_table(tablename, 'UID', uid):
            z = ['{}={}'.format(f.getName(),
                                self._mutate(f, values[f.getName()]))
                 for f in fields]
            query = uq.format(tablename, ','.join(z), uid)
        else:
            colnames = ['UID', 'PARENTUID'] + [f.getName() for f in fields]
            colvals = ["'{}','{}'".format(uid, p_uid)] + \
                      [self._mutate(f, values[f.getName()]) for f in fields]
            query = iq.format(tablename, ','.join(colnames), ','.join(colvals))
        queries.append(query)

        # Dict field types, insert or update lookup value table
        uq = "UPDATE {} SET {} WHERE {}_UID='{}'"
        iq = "INSERT INTO {} ({}_UID, {}) VALUES ('{}', {})"
        for field in dict_fields:
            fieldname = field.getName()
            tablename = "{}_{}".format(ptname, fieldname)
            dict_val = values[fieldname]
            if isinstance(dict_val, dict):
                dict_val = [dict_val]
            for dval in dict_val:
                colnames = field.subfields
                colvals = ["'{}'".format(_e(dval.get(colname, '')))
                           for colname in colnames]
                col = '{}_UID'.format(ptname)
                if self.exists_in_table(tablename, col, uid):
                    z = ['{}={}'.format(*x) for x in zip(colnames, colvals)]
                    query = uq.format(tablename, ','.join(z), ptname, uid)
                else:
                    query = iq.format(tablename, ptname, ','.join(colnames),
                                      uid, ','.join(colvals))
                queries.append(query)

        # List field types, insert or update lookup value table
        iq = "INSERT INTO {} (value, {}_UID) VALUES ('{}', '{}')"
        uq = "UPDATE {} SET value='{}' WHERE {}_UID='{}'"
        for field in list_fields:
            fieldname = field.getName()
            tablename = "{}_{}".format(ptname, fieldname)
            list_val = values[fieldname]
            if type(list_val) not in (list, tuple):
                list_val = list(list_val)
            for lval in list_val:
                col = '{}_UID'.format(ptname)
                if self.exists_in_table(tablename, col, uid):
                    query = uq.format(tablename, _e(lval), ptname, uid)
                else:
                    query = iq.format(tablename, ptname, _e(lval), uid)
                queries.append(query)

        return queries

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
            # noinspection PyStatementEffect
            cur.fetchmany(1)[0]
        except IndexError:
            return False
        finally:
            self.conn.rollback()
        return True

    def get_fields(self, schema, values=None):
        """Get only fields from instance schema that use the BikaSQLStorage.
        Some really specific things for some types of fields are in here.
        
        :param schema: AT schema containing BikaSQLStorage fields.
        :type schema: Schema
        :param values: Dictionary of values.  If present, only fields which
        have corresponding keys in this dict will be returned.
        :type values: dict
        :return: A list of schema field objects
        :rtype: list
        """

        dict_fields = []
        list_fields = []
        fields = []  # single-valued fields

        allfields = []
        for field in schema.fields():
            if IObjectField.providedBy(field) \
                    and (hasattr(field, 'getStorage')  # ComputedField
                         and field.getStorage() == BikaSQLStorage()):
                if values and field.getName() not in values:
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

    def _coltype(self, field):
        """Return a column type which will store values from this field.

        :param field: A schema field who's type will be used.
        :type field: ObjectField
        """
        fieldtype = field.type
        nt = self.type_map.get(fieldtype, 'TEXT')
        return nt

    def _mutate(self, field, value):
        """Return the field value, escaped and quoted to fit the column.
        
        :param field: A schema field who's value we want to return.
        :type field: ObjectField
        :param value: Value passed to us from SQL_QUEUE 
        :type value: Any
        :return: quoted/mutated string
        :rtype: string
        """
        mutator = getattr(FieldMutators,
                          'mutate_{}'.format(field.type),
                          FieldMutators.mutate_str)
        value = mutator(value)
        return value


class FieldMutators:
    def __init__(self):
        pass

    @staticmethod
    def mutate_lines(value):
        """LinesField values as a single string with newlines as separater

        :param value: LinesField value
        :type value: list | tuple
        :return: escaped quoted string
        :rtype: string
        """
        if value:
            value = _e("{}".format('\n'.join(value)))
            return "'{}'".format(value)
        return 'NULL'

    @staticmethod
    def mutate_datetime(value):
        """DateTime value is ISO string or NULL if no date is set.

        :param value: DateTimeField value
        :type value: DateTime
        :return: escaped quoted string
        :rtype: string
        """
        if value:
            return "'{}'".format(_e(value.ISO()))
        return "NULL"

    @staticmethod
    def mutate_blob(value):
        """Write the path to the location of the file data in blobstorage

        :param value: blobfield value
        :type value: BlobWrapper
        :return: quoted string
        :rtype: string
        """
        if value:
            return "'{}'".format(value.blob.committed())
        return 'NULL'

    @staticmethod
    def mutate_str(value):
        """Default field handler; just wraps in quotes.

        :param value: blobfield value
        :type value: BlobWrapper
        :return: escaped quoted string
        :rtype: string
        """
        if value:
            return "'{}'".format(_e(value))
        return 'NULL'

    @staticmethod
    def mutate_int(value):
        """Just the value, no quotes

        :param value: IntegerField field value
        :type value: int
        :return: escaped quoted string
        :rtype: string
        """
        if value:
            return _e("{}".format(value))
        return 'NULL'

    @staticmethod
    def mutate_float(value):
        """Just the value, no quotes

        :param value: FloatField field value
        :type value: float
        :return: escaped quoted string
        :rtype: string
        """
        if value:
            return _e("{}".format(value))
        return 'NULL'


def _e(value):
    """Dead simple escape, no quotes.

    :param value: string
    :type value: string
    :return: escaped string
    :rtype: string
    """
    value = str(value)
    value = value.replace('\'', '')
    value = value.replace('"', '')
    return value
