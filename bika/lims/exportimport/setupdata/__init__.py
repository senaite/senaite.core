# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import datetime
import os.path
import re

from pkg_resources import resource_filename

import transaction
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.exportimport.dataimport import SetupDataSetList as SDL
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import ISetupDataSetList
from bika.lims.utils import getFromString
from bika.lims.utils import t
from bika.lims.utils import tmpID
from bika.lims.utils import to_unicode
from bika.lims.utils.analysis import create_analysis
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from zope.event import notify
from zope.interface import implements


def lookup(context, portal_type, **kwargs):
    at = getToolByName(context, 'archetype_tool')
    catalog = at.catalog_map.get(portal_type, [None])[0] or 'portal_catalog'
    catalog = getToolByName(context, catalog)
    kwargs['portal_type'] = portal_type
    return catalog(**kwargs)[0].getObject()


def check_for_required_columns(name, data, required):
    for column in required:
        if not data.get(column, None):
            message = _("%s has no '%s' column." % (name, column))
            raise Exception(t(message))


def Float(thing):
    try:
        f = float(thing)
    except ValueError:
        f = 0.0
    return f


def read_file(path):
    if os.path.isfile(path):
        return open(path, "rb").read()
    allowed_ext = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'ods', 'odt',
                   'xlsx', 'doc', 'docx', 'xls', 'csv', 'txt']
    allowed_ext += [e.upper() for e in allowed_ext]
    for e in allowed_ext:
        out = '%s.%s' % (path, e)
        if os.path.isfile(out):
            return open(out, "rb").read()
    raise IOError("File not found: %s. Allowed extensions: %s" % (path, ','.join(allowed_ext)))


class SetupDataSetList(SDL):

    implements(ISetupDataSetList)

    def __call__(self):
        return SDL.__call__(self, projectname="bika.lims")


class WorksheetImporter:

    """Use this as a base, for normal tabular data sheet imports.
    """

    def __init__(self, context):
        self.adapter_context = context

    def __call__(self, lsd, workbook, dataset_project, dataset_name):
        self.lsd = lsd
        self.context = lsd.context
        self.workbook = workbook
        self.sheetname = self.__class__.__name__.replace("_", " ")
        self.worksheet = workbook.get_sheet_by_name(self.sheetname)
        self.dataset_project = dataset_project
        self.dataset_name = dataset_name
        if self.worksheet:
            logger.info("Loading {0}.{1}: {2}".format(
                self.dataset_project, self.dataset_name, self.sheetname))
            try:
                self.Import()
            except IOError:
                # The importer must omit the files not found inside the server filesystem (bika/lims/setupdata/test/
                # if the file is loaded from 'select existing file' or bika/lims/setupdata/uploaded if it's loaded from
                # 'Load from file') and finishes the import without errors. https://jira.bikalabs.com/browse/LIMS-1624
                warning = "Error while loading attached file from %s. The file will not be uploaded into the system."
                logger.warning(warning, self.sheetname)
                self.context.plone_utils.addPortalMessage("Error while loading some attached files. "
                                                          "The files weren't uploaded into the system.")
        else:
            logger.info("No records found: '{0}'".format(self.sheetname))

    def get_rows(self, startrow=3, worksheet=None):
        """Returns a generator for all rows in a sheet.
           Each row contains a dictionary where the key is the value of the
           first row of the sheet for each column.
           The data values are returned in utf-8 format.
           Starts to consume data from startrow
        """

        headers = []
        row_nr = 0
        worksheet = worksheet if worksheet else self.worksheet
        for row in worksheet.rows:  # .iter_rows():
            row_nr += 1
            if row_nr == 1:
                # headers = [cell.internal_value for cell in row]
                headers = [cell.value for cell in row]
                continue
            if row_nr % 1000 == 0:
                transaction.savepoint()
            if row_nr <= startrow:
                continue
            # row = [_c(cell.internal_value).decode('utf-8') for cell in row]
            new_row = []
            for cell in row:
                value = cell.value
                if value is None:
                    value = ''
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
                # Strip any space, \t, \n, or \r characters from the left-hand
                # side, right-hand side, or both sides of the string
                if isinstance(value, str):
                    value = value.strip(' \t\n\r')
                new_row.append(value)
            row = dict(zip(headers, new_row))

            # parse out addresses
            for add_type in ['Physical', 'Postal', 'Billing']:
                row[add_type] = {}
                if add_type + "_Address" in row:
                    for key in ['Address', 'City', 'State', 'District', 'Zip', 'Country']:
                        row[add_type][key] = str(row.get("%s_%s" % (add_type, key), ''))

            yield row

    def get_file_data(self, filename):
        if filename:
            try:
                path = resource_filename(
                    self.dataset_project,
                    "setupdata/%s/%s" % (self.dataset_name, filename))
                file_data = open(path, "rb").read()
            except:
                file_data = None
        else:
            file_data = None
        return file_data

    def to_bool(self, value):
        """ Converts a sheet string value to a boolean value.
            Needed because of utf-8 conversions
        """

        try:
            value = value.lower()
        except:
            pass
        try:
            value = value.encode('utf-8')
        except:
            pass
        try:
            value = int(value)
        except:
            pass
        if value in ('true', 1):
            return True
        else:
            return False

    def to_int(self, value, default=0):
        """ Converts a value o a int. Returns default if the conversion fails.
        """
        try:
            return int(value)
        except ValueError:
            try:
                return int(default)
            except:
                return 0

    def to_float(self, value, default=0):
        """ Converts a value o a float. Returns default if the conversion fails.
        """
        try:
            return float(value)
        except ValueError:
            try:
                return float(default)
            except:
                return 0.0

    def defer(self, **kwargs):
        self.lsd.deferred.append(kwargs)

    def Import(self):
        """ Override this.
        XXX Simple generic sheet importer
        """

    def fill_addressfields(self, row, obj):
        """ Fills the address fields for the specified object if allowed:
            PhysicalAddress, PostalAddress, CountryState, BillingAddress
        """
        addresses = {}
        for add_type in ['Physical', 'Postal', 'Billing', 'CountryState']:
            addresses[add_type] = {}
            for key in ['Address', 'City', 'State', 'District', 'Zip', 'Country']:
                addresses[add_type][key.lower()] = str(row.get("%s_%s" % (add_type, key), ''))

        if addresses['CountryState']['country'] == '' \
            and addresses['CountryState']['state'] == '':
            addresses['CountryState']['country'] = addresses['Physical']['country']
            addresses['CountryState']['state'] = addresses['Physical']['state']

        if hasattr(obj, 'setPhysicalAddress'):
            obj.setPhysicalAddress(addresses['Physical'])
        if hasattr(obj, 'setPostalAddress'):
            obj.setPostalAddress(addresses['Postal'])
        if hasattr(obj, 'setCountryState'):
            obj.setCountryState(addresses['CountryState'])
        if hasattr(obj, 'setBillingAddress'):
            obj.setBillingAddress(addresses['Billing'])

    def fill_contactfields(self, row, obj):
        """ Fills the contact fields for the specified object if allowed:
            EmailAddress, Phone, Fax, BusinessPhone, BusinessFax, HomePhone,
            MobilePhone
        """
        fieldnames = ['EmailAddress',
                      'Phone',
                      'Fax',
                      'BusinessPhone',
                      'BusinessFax',
                      'HomePhone',
                      'MobilePhone',
                      ]
        schema = obj.Schema()
        fields = dict([(field.getName(), field) for field in schema.fields()])
        for fieldname in fieldnames:
            try:
                field = fields[fieldname]
            except:
                if fieldname in row:
                    logger.info("Address field %s not found on %s"%(fieldname,obj))
                continue
            value = row.get(fieldname, '')
            field.set(obj, value)

    def get_object(self, catalog, portal_type, title=None, **kwargs):
        """This will return an object from the catalog.
        Logs a message and returns None if no object or multiple objects found.
        All keyword arguments are passed verbatim to the contentFilter
        """
        if not title and not kwargs:
            return None
        contentFilter = {"portal_type": portal_type}
        if title:
            contentFilter['title'] = to_unicode(title)
        contentFilter.update(kwargs)
        brains = catalog(contentFilter)
        if len(brains) > 1:
            logger.info("More than one object found for %s" % contentFilter)
            return None
        elif len(brains) == 0:
            if portal_type == 'AnalysisService':
                brains = catalog(portal_type=portal_type, getKeyword=title)
                if brains:
                    return brains[0].getObject()
            logger.info("No objects found for %s" % contentFilter)
            return None
        else:
            return brains[0].getObject()


class Sub_Groups(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_subgroups
        for row in self.get_rows(3):
            if 'title' in row and row['title']:
                obj = _createObjectByType("SubGroup", folder, tmpID())
                obj.edit(title=row['title'],
                         description=row['description'],
                         SortKey=row['SortKey'])
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Lab_Information(WorksheetImporter):

    def Import(self):
        laboratory = self.context.bika_setup.laboratory
        values = {}
        for row in self.get_rows(3):
            values[row['Field']] = row['Value']

        if values['AccreditationBodyLogo']:
            path = resource_filename(
                self.dataset_project,
                "setupdata/%s/%s" % (self.dataset_name,
                                     values['AccreditationBodyLogo']))
            try:
                file_data = read_file(path)
            except Exception as msg:
                file_data = None
                logger.warning(msg[0] + " Error on sheet: " + self.sheetname)
        else:
            file_data = None

        laboratory.edit(
            Name=values['Name'],
            LabURL=values['LabURL'],
            Confidence=values['Confidence'],
            LaboratoryAccredited=self.to_bool(values['LaboratoryAccredited']),
            AccreditationBodyLong=values['AccreditationBodyLong'],
            AccreditationBody=values['AccreditationBody'],
            AccreditationBodyURL=values['AccreditationBodyURL'],
            Accreditation=values['Accreditation'],
            AccreditationReference=values['AccreditationReference'],
            AccreditationBodyLogo=file_data,
            TaxNumber=values['TaxNumber'],
        )
        self.fill_contactfields(values, laboratory)
        self.fill_addressfields(values, laboratory)


class Lab_Contacts(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_labcontacts
        portal_groups = getToolByName(self.context, 'portal_groups')
        portal_registration = getToolByName(
            self.context, 'portal_registration')
        rownum = 2
        for row in self.get_rows(3):
            rownum+=1
            if not row.get('Firstname',None):
                continue

            # Username already exists?
            username = row.get('Username','')
            fullname = ('%s %s' % (row['Firstname'], row.get('Surname', ''))).strip()
            if username:
                username = safe_unicode(username).encode('utf-8')
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                exists = [o.getObject() for o in bsc(portal_type="LabContact") if o.getObject().getUsername()==username]
                if exists:
                    error = "Lab Contact: username '{0}' in row {1} already exists. This contact will be omitted.".format(username, str(rownum))
                    logger.error(error)
                    continue

            # Is there a signature file defined? Try to get the file first.
            signature = None
            if row.get('Signature'):
                signature = self.get_file_data(row['Signature'])
                if not signature:
                    warning = "Lab Contact: Cannot load the signature file '{0}' for user '{1}'. The contact will be created, but without a signature image".format(row['Signature'], username)
                    logger.warning(warning)

            obj = _createObjectByType("LabContact", folder, tmpID())
            obj.edit(
                title=fullname,
                Salutation=row.get('Salutation', ''),
                Firstname=row['Firstname'],
                Surname=row.get('Surname', ''),
                JobTitle=row.get('JobTitle', ''),
                Username=row.get('Username', ''),
                Signature=signature
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))
            self.fill_contactfields(row, obj)
            self.fill_addressfields(row, obj)

            if row['Department_title']:
                self.defer(src_obj=obj,
                           src_field='Department',
                           dest_catalog='bika_setup_catalog',
                           dest_query={'portal_type': 'Department',
                                       'title': row['Department_title']}
                           )

            # Create Plone user
            if not row['Username']:
                warn = "Lab Contact: No username defined for user '{0}' in row {1}. Contact created, but without access credentials.".format(fullname, str(rownum))
                logger.warning(warn)
            if not row.get('EmailAddress', ''):
                warn = "Lab Contact: No Email defined for user '{0}' in row {1}. Contact created, but without access credentials.".format(fullname, str(rownum))
                logger.warning(warn)

            if(row['Username'] and row.get('EmailAddress','')):
                username = safe_unicode(row['Username']).encode('utf-8')
                passw = row['Password']
                if not passw:
                    warn = "Lab Contact: No password defined for user '{0}' in row {1}. Password established automatically to '{3}'".format(username, str(rownum), username)
                    logger.warning(warn)
                    passw = username

                try:
                    member = portal_registration.addMember(
                        username,
                        passw,
                        properties={
                            'username': username,
                            'email': row['EmailAddress'],
                            'fullname': fullname}
                    )
                except Exception as msg:
                    logger.error("Client Contact: Error adding user (%s): %s" % (msg, username))
                    continue

                groups = row.get('Groups', '')
                if not groups:
                    warn = "Lab Contact: No groups defined for user '{0}' in row {1}. Group established automatically to 'Analysts'".format(username, str(rownum))
                    logger.warning(warn)
                    groups = 'Analysts'

                group_ids = [g.strip() for g in groups.split(',')]
                # Add user to all specified groups
                for group_id in group_ids:
                    group = portal_groups.getGroupById(group_id)
                    if group:
                        group.addMember(username)
                roles = row.get('Roles', '')
                if roles:
                    role_ids = [r.strip() for r in roles.split(',')]
                    # Add user to all specified roles
                    for role_id in role_ids:
                        member._addRole(role_id)
                # If user is in LabManagers, add Owner local role on clients
                # folder
                if 'LabManager' in group_ids:
                    self.context.clients.manage_setLocalRoles(
                        username, ['Owner', ])

        # Now we have the lab contacts registered, try to assign the managers
        # to each department if required
        sheet = self.workbook.get_sheet_by_name("Lab Departments")
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, sheet):
            if row['title'] and row['LabContact_Username']:
                dept = self.get_object(bsc, "Department", row.get('title'))
                if dept and not dept.getManager():
                    username = safe_unicode(row['LabContact_Username']).encode('utf-8')
                    exists = [o.getObject() for o in bsc(portal_type="LabContact") if o.getObject().getUsername()==username]
                    if exists:
                        dept.setManager(exists[0].UID())

class Lab_Departments(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_departments
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        lab_contacts = [o.getObject() for o in bsc(portal_type="LabContact")]
        for row in self.get_rows(3):
            if row['title']:
                obj = _createObjectByType("Department", folder, tmpID())
                obj.edit(title=row['title'],
                         description=row.get('description', ''))
                manager = None
                for contact in lab_contacts:
                    if contact.getUsername() == row['LabContact_Username']:
                        manager = contact
                        break
                if manager:
                    obj.setManager(manager.UID())
                else:
                    message = "Department: lookup of '%s' in LabContacts/Username failed." % row[
                        'LabContact_Username']
                    logger.info(message)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Lab_Products(WorksheetImporter):

    def Import(self):
        context = self.context
        # Refer to the default folder
        folder = self.context.bika_setup.bika_labproducts
        # Iterate through the rows
        for row in self.get_rows(3):
            # Create the LabProduct object
            obj = _createObjectByType('LabProduct', folder, tmpID())
            # Apply the row values
            obj.edit(
                title=row.get('title', 'Unknown'),
                description=row.get('description', ''),
                Volume=row.get('volume', 0),
                Unit=str(row.get('unit', 0)),
                Price=str(row.get('price', 0)),
            )
            # Rename the new object
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Clients(WorksheetImporter):

    def Import(self):
        folder = self.context.clients
        for row in self.get_rows(3):
            obj = _createObjectByType("Client", folder, tmpID())
            if not row['Name']:
                message = "Client %s has no Name"
                raise Exception(message)
            if not row['ClientID']:
                message = "Client %s has no Client ID"
                raise Exception(message)
            obj.edit(Name=row['Name'],
                     ClientID=row['ClientID'],
                     MemberDiscountApplies=row[
                         'MemberDiscountApplies'] and True or False,
                     BulkDiscount=row['BulkDiscount'] and True or False,
                     TaxNumber=row.get('TaxNumber', ''),
                     AccountNumber=row.get('AccountNumber', '')
                     )
            self.fill_contactfields(row, obj)
            self.fill_addressfields(row, obj)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Client_Contacts(WorksheetImporter):

    def Import(self):
        portal_groups = getToolByName(self.context, 'portal_groups')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            client = pc(portal_type="Client",
                        getName=row['Client_title'])
            if len(client) == 0:
                client_contact = "%(Firstname)s %(Surname)s" % row
                error = "Client invalid: '%s'. The Client Contact %s will not be uploaded."
                logger.error(error, row['Client_title'], client_contact)
                continue
            client = client[0].getObject()
            contact = _createObjectByType("Contact", client, tmpID())
            fullname = "%(Firstname)s %(Surname)s" % row
            pub_pref = [x.strip() for x in
                        row.get('PublicationPreference', '').split(",")]
            contact.edit(
                Salutation=row.get('Salutation', ''),
                Firstname=row.get('Firstname', ''),
                Surname=row.get('Surname', ''),
                Username=row['Username'],
                JobTitle=row.get('JobTitle', ''),
                Department=row.get('Department', ''),
                PublicationPreference=pub_pref,
                AttachmentsPermitted=row[
                    'AttachmentsPermitted'] and True or False,
            )
            self.fill_contactfields(row, contact)
            self.fill_addressfields(row, contact)
            contact.unmarkCreationFlag()
            renameAfterCreation(contact)
            notify(ObjectInitializedEvent(contact))
            # CC Contacts
            if row['CCContacts']:
                names = [x.strip() for x in row['CCContacts'].split(",")]
                for _fullname in names:
                    self.defer(src_obj=contact,
                               src_field='CCContact',
                               dest_catalog='portal_catalog',
                               dest_query={'portal_type': 'Contact',
                                           'getFullname': _fullname}
                               )
            ## Create Plone user
            username = safe_unicode(row['Username']).encode('utf-8')
            password = safe_unicode(row['Password']).encode('utf-8')
            if(username):
                try:
                    member = self.context.portal_registration.addMember(
                        username,
                        password,
                        properties={
                            'username': username,
                            'email': row['EmailAddress'],
                            'fullname': fullname}
                        )
                except Exception as msg:
                    logger.info("Error adding user (%s): %s" % (msg, username))
                contact.aq_parent.manage_setLocalRoles(row['Username'], ['Owner', ])
                contact.reindexObject()
                # add user to Clients group
                group = portal_groups.getGroupById('Clients')
                group.addMember(username)


class Container_Types(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_containertypes
        for row in self.get_rows(3):
            if not row['title']:
                continue
            obj = _createObjectByType("ContainerType", folder, tmpID())
            obj.edit(title=row['title'],
                     description=row.get('description', ''))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Preservations(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_preservations
        for row in self.get_rows(3):
            if not row['title']:
                continue
            obj = _createObjectByType("Preservation", folder, tmpID())
            RP = {
                'days': int(row['RetentionPeriod_days'] and row['RetentionPeriod_days'] or 0),
                'hours': int(row['RetentionPeriod_hours'] and row['RetentionPeriod_hours'] or 0),
                'minutes': int(row['RetentionPeriod_minutes'] and row['RetentionPeriod_minutes'] or 0),
            }

            obj.edit(title=row['title'],
                     description=row.get('description', ''),
                     RetentionPeriod=RP)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Containers(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_containers
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue
            obj = _createObjectByType("Container", folder, tmpID())
            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Capacity=row.get('Capacity', 0),
                PrePreserved=self.to_bool(row['PrePreserved'])
            )
            if row['ContainerType_title']:
                ct = self.get_object(bsc, 'ContainerType', row.get('ContainerType_title',''))
                if ct:
                    obj.setContainerType(ct)
            if row['Preservation_title']:
                pres = self.get_object(bsc, 'Preservation',row.get('Preservation_title',''))
                if pres:
                    obj.setPreservation(pres)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Suppliers(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_suppliers
        for row in self.get_rows(3):
            obj = _createObjectByType("Supplier", folder, tmpID())
            if row['Name']:
                obj.edit(
                    Name=row.get('Name', ''),
                    TaxNumber=row.get('TaxNumber', ''),
                    AccountType=row.get('AccountType', {}),
                    AccountName=row.get('AccountName', {}),
                    AccountNumber=row.get('AccountNumber', ''),
                    BankName=row.get('BankName', ''),
                    BankBranch=row.get('BankBranch', ''),
                    SWIFTcode=row.get('SWIFTcode', ''),
                    IBN=row.get('IBN', ''),
                    NIB=row.get('NIB', ''),
                    Website=row.get('Website', ''),
                )
                self.fill_contactfields(row, obj)
                self.fill_addressfields(row, obj)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Supplier_Contacts(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['Supplier_Name']:
                continue
            if not row['Firstname']:
                continue
            folder = bsc(portal_type="Supplier",
                         Title=row['Supplier_Name'])
            if not folder:
                continue
            folder = folder[0].getObject()
            obj = _createObjectByType("SupplierContact", folder, tmpID())
            obj.edit(
                Firstname=row['Firstname'],
                Surname=row.get('Surname', ''),
                Username=row.get('Username')
            )
            self.fill_contactfields(row, obj)
            self.fill_addressfields(row, obj)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Manufacturers(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_manufacturers
        for row in self.get_rows(3):
            obj = _createObjectByType("Manufacturer", folder, tmpID())
            if row['title']:
                obj.edit(
                    title=row['title'],
                    description=row.get('description', '')
                )
                self.fill_addressfields(row, obj)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Instrument_Types(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_instrumenttypes
        for row in self.get_rows(3):
                obj = _createObjectByType("InstrumentType", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''))
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Instruments(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_instruments
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            if ('Type' not in row
                or 'Supplier' not in row
                or 'Brand' not in row):
                logger.info("Unable to import '%s'. Missing supplier, manufacturer or type" % row.get('title',''))
                continue

            obj = _createObjectByType("Instrument", folder, tmpID())

            obj.edit(
                title=row.get('title', ''),
                AssetNumber=row.get('assetnumber', ''),
                description=row.get('description', ''),
                Type=row.get('Type', ''),
                Brand=row.get('Brand', ''),
                Model=row.get('Model', ''),
                SerialNo=row.get('SerialNo', ''),
                DataInterface=row.get('DataInterface', ''),
                Location=row.get('Location', ''),
                InstallationDate=row.get('Instalationdate', ''),
                UserManualID=row.get('UserManualID', ''),
            )
            instrumenttype = self.get_object(bsc, 'InstrumentType', title=row.get('Type'))
            manufacturer = self.get_object(bsc, 'Manufacturer', title=row.get('Brand'))
            supplier = self.get_object(bsc, 'Supplier', getName=row.get('Supplier', ''))
            method = self.get_object(pc, 'Method', title=row.get('Method'))
            obj.setInstrumentType(instrumenttype)
            obj.setManufacturer(manufacturer)
            obj.setSupplier(supplier)
            if method:
                obj.setMethods([method])
                obj.setMethod(method)

            # Attaching the instrument's photo
            if row.get('Photo', None):
                path = resource_filename(
                    self.dataset_project,
                    "setupdata/%s/%s" % (self.dataset_name,
                                         row['Photo'])
                )
                try:
                    file_data = read_file(path)
                    obj.setPhoto(file_data)
                except Exception as msg:
                    file_data = None
                    logger.warning(msg[0] + " Error on sheet: " + self.sheetname)

            # Attaching the Installation Certificate if exists
            if row.get('InstalationCertificate', None):
                path = resource_filename(
                    self.dataset_project,
                    "setupdata/%s/%s" % (self.dataset_name,
                                         row['InstalationCertificate'])
                )
                try:
                    file_data = read_file(path)
                    obj.setInstallationCertificate(file_data)
                except Exception as msg:
                    logger.warning(msg[0] + " Error on sheet: " + self.sheetname)

            # Attaching the Instrument's manual if exists
            if row.get('UserManualFile', None):
                row_dict = {'DocumentID': row.get('UserManualID', 'manual'),
                            'DocumentVersion': '',
                            'DocumentLocation': '',
                            'DocumentType': 'Manual',
                            'File': row.get('UserManualFile', None)
                            }
                addDocument(self, row_dict, obj)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Instrument_Validations(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row.get('instrument', None) or not row.get('title', None):
                continue

            folder = self.get_object(bsc, 'Instrument', row.get('instrument'))
            if folder:
                obj = _createObjectByType("InstrumentValidation", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    DownFrom=row.get('downfrom', ''),
                    DownTo=row.get('downto', ''),
                    Validator=row.get('validator', ''),
                    Considerations=row.get('considerations', ''),
                    WorkPerformed=row.get('workperformed', ''),
                    Remarks=row.get('remarks', ''),
                    DateIssued=row.get('DateIssued', ''),
                    ReportID=row.get('ReportID', '')
                )
                # Getting lab contacts
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                lab_contacts = [o.getObject() for o in bsc(portal_type="LabContact", is_active=True)]
                for contact in lab_contacts:
                    if contact.getFullname() == row.get('Worker', ''):
                        obj.setWorker(contact.UID())
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Instrument_Calibrations(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row.get('instrument', None) or not row.get('title', None):
                continue

            folder = self.get_object(bsc, 'Instrument', row.get('instrument'))
            if folder:
                obj = _createObjectByType("InstrumentCalibration", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    DownFrom=row.get('downfrom', ''),
                    DownTo=row.get('downto', ''),
                    Calibrator=row.get('calibrator', ''),
                    Considerations=row.get('considerations', ''),
                    WorkPerformed=row.get('workperformed', ''),
                    Remarks=row.get('remarks', ''),
                    DateIssued=row.get('DateIssued', ''),
                    ReportID=row.get('ReportID', '')
                )
                # Gettinginstrument lab contacts
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                lab_contacts = [o.getObject() for o in bsc(portal_type="LabContact", nactive_state='active')]
                for contact in lab_contacts:
                    if contact.getFullname() == row.get('Worker', ''):
                        obj.setWorker(contact.UID())
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Instrument_Certifications(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['instrument'] or not row['title']:
                continue

            folder = self.get_object(bsc, 'Instrument', row.get('instrument',''))
            if folder:
                obj = _createObjectByType("InstrumentCertification", folder, tmpID())
                today = datetime.date.today()
                certificate_expire_date = today.strftime('%d/%m') + '/' + str(today.year+1) \
                    if row.get('validto', '') == '' else row.get('validto')
                certificate_start_date = today.strftime('%d/%m/%Y') \
                    if row.get('validfrom', '') == '' else row.get('validfrom')
                obj.edit(
                    title=row['title'],
                    AssetNumber=row.get('assetnumber', ''),
                    Date=row.get('date', ''),
                    ValidFrom=certificate_start_date,
                    ValidTo=certificate_expire_date,
                    Agency=row.get('agency', ''),
                    Remarks=row.get('remarks', ''),
                )
                # Attaching the Report Certificate if exists
                if row.get('report', None):
                    path = resource_filename(
                        self.dataset_project,
                        "setupdata/%s/%s" % (self.dataset_name,
                                             row['report'])
                    )
                    try:
                        file_data = read_file(path)
                        obj.setDocument(file_data)
                    except Exception as msg:
                        file_data = None
                        logger.warning(msg[0] + " Error on sheet: " + self.sheetname)

                # Getting lab contacts
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                lab_contacts = [o.getObject() for o in bsc(portal_type="LabContact", nactive_state='active')]
                for contact in lab_contacts:
                    if contact.getFullname() == row.get('preparedby', ''):
                        obj.setPreparator(contact.UID())
                    if contact.getFullname() == row.get('approvedby', ''):
                        obj.setValidator(contact.UID())
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Instrument_Documents(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row.get('instrument', ''):
                continue
            folder = self.get_object(bsc, 'Instrument', row.get('instrument', ''))
            addDocument(self, row, folder)

def addDocument(self, row_dict, folder):
    """
    This function adds a multifile object to the instrument folder
    :param row_dict: the dictionary which contains the document information
    :param folder: the instrument object
    """
    if folder:
        # This content type need a file
        if row_dict.get('File', None):
            path = resource_filename(
                self.dataset_project,
                "setupdata/%s/%s" % (self.dataset_name,
                                     row_dict['File'])
            )
            try:
                file_data = read_file(path)
            except Exception as msg:
                file_data = None
                logger.warning(msg[0] + " Error on sheet: " + self.sheetname)

            # Obtain all created instrument documents content type
            catalog = getToolByName(self.context, 'bika_setup_catalog')
            documents_brains = catalog.searchResults({'portal_type': 'Multifile'})
            # If a the new document has the same DocumentID as a created document, this object won't be created.
            idAlreadyInUse = False
            for item in documents_brains:
                if item.getObject().getDocumentID() == row_dict.get('DocumentID', ''):
                    warning = "The ID '%s' used for this document is already in use on instrument '%s', consequently " \
                              "the file hasn't been upload." % (row_dict.get('DocumentID', ''), row_dict.get('instrument', ''))
                    self.context.plone_utils.addPortalMessage(warning)
                    idAlreadyInUse = True
            if not idAlreadyInUse:
                obj = _createObjectByType("Multifile", folder, tmpID())
                obj.edit(
                    DocumentID=row_dict.get('DocumentID', ''),
                    DocumentVersion=row_dict.get('DocumentVersion', ''),
                    DocumentLocation=row_dict.get('DocumentLocation', ''),
                    DocumentType=row_dict.get('DocumentType', ''),
                    File=file_data
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Instrument_Maintenance_Tasks(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['instrument'] or not row['title'] or not row['type']:
                continue

            folder = self.get_object(bsc, 'Instrument',row.get('instrument'))
            if folder:
                obj = _createObjectByType("InstrumentMaintenanceTask", folder, tmpID())
                try:
                    cost = "%.2f" % (row.get('cost', 0))
                except:
                    cost = row.get('cost', '0.0')

                obj.edit(
                    title=row['title'],
                    description=row['description'],
                    Type=row['type'],
                    DownFrom=row.get('downfrom', ''),
                    DownTo=row.get('downto', ''),
                    Maintainer=row.get('maintaner', ''),
                    Considerations=row.get('considerations', ''),
                    WorkPerformed=row.get('workperformed', ''),
                    Remarks=row.get('remarks', ''),
                    Cost=cost,
                    Closed=self.to_bool(row.get('closed'))
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Instrument_Schedule(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['instrument'] or not row['title'] or not row['type']:
                continue
            folder = self.get_object(bsc, 'Instrument', row.get('instrument'))
            if folder:
                obj = _createObjectByType("InstrumentScheduledTask", folder, tmpID())
                criteria = [
                    {'fromenabled': row.get('date', None) is not None,
                     'fromdate': row.get('date', ''),
                     'repeatenabled': ((row['numrepeats'] and
                                        row['numrepeats'] > 1) or
                                       (row['repeatuntil'] and
                                        len(row['repeatuntil']) > 0)),
                     'repeatunit': row.get('numrepeats', ''),
                     'repeatperiod': row.get('periodicity', ''),
                     'repeatuntilenabled': (row['repeatuntil'] and
                                            len(row['repeatuntil']) > 0),
                     'repeatuntil': row.get('repeatuntil')}
                ]
                obj.edit(
                    title=row['title'],
                    Type=row['type'],
                    ScheduleCriteria=criteria,
                    Considerations=row.get('considerations', ''),
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Sample_Matrices(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_samplematrices
        for row in self.get_rows(3):
            if not row['title']:
                continue
            obj = _createObjectByType("SampleMatrix", folder, tmpID())
            obj.edit(
                title=row['title'],
                description=row.get('description', '')
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Batch_Labels(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_batchlabels
        for row in self.get_rows(3):
            if row['title']:
                obj = _createObjectByType("BatchLabel", folder, tmpID())
                obj.edit(title=row['title'])
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Sample_Types(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_sampletypes
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue
            obj = _createObjectByType("SampleType", folder, tmpID())
            samplematrix = self.get_object(bsc, 'SampleMatrix',
                                           row.get('SampleMatrix_title'))
            containertype = self.get_object(bsc, 'ContainerType',
                                            row.get('ContainerType_title'))
            retentionperiod = {
                'days': row['RetentionPeriod'] if row['RetentionPeriod'] else 0,
                'hours': 0,
                'minutes': 0}
            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                RetentionPeriod=retentionperiod,
                Hazardous=self.to_bool(row['Hazardous']),
                SampleMatrix=samplematrix,
                Prefix=row['Prefix'],
                MinimumVolume=row['MinimumVolume'],
                ContainerType=containertype
            )
            samplepoint = self.get_object(bsc, 'SamplePoint',
                                          row.get('SamplePoint_title'))
            if samplepoint:
                samplepoint.setSampleType([obj, ])
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Sample_Points(WorksheetImporter):

    def Import(self):
        setup_folder = self.context.bika_setup.bika_samplepoints
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue
            if row['Client_title']:
                client_title = row['Client_title']
                client = pc(portal_type="Client", getName=client_title)
                if len(client) == 0:
                    error = "Sample Point %s: Client invalid: '%s'. The Sample point will not be uploaded."
                    logger.error(error, row['title'], client_title)
                    continue
                folder = client[0].getObject()
            else:
                folder = setup_folder

            if row['Latitude']:
                logger.log("Ignored SamplePoint Latitude", 'error')
            if row['Longitude']:
                logger.log("Ignored SamplePoint Longitude", 'error')

            obj = _createObjectByType("SamplePoint", folder, tmpID())
            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Composite=self.to_bool(row['Composite']),
                Elevation=row['Elevation'],
            )
            sampletype = self.get_object(bsc, 'SampleType',
                                         row.get('SampleType_title'))
            if sampletype:
                obj.setSampleTypes([sampletype, ])
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Sample_Point_Sample_Types(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            sampletype = self.get_object(bsc,
                                         'SampleType',
                                         row.get('SampleType_title'))
            samplepoint = self.get_object(bsc,
                                          'SamplePoint',
                                          row['SamplePoint_title'])
            if samplepoint:
                sampletypes = samplepoint.getSampleTypes()
                if sampletype not in sampletypes:
                    sampletypes.append(sampletype)
                    samplepoint.setSampleTypes(sampletypes)


class Storage_Locations(WorksheetImporter):

    def Import(self):
        setup_folder = self.context.bika_setup.bika_storagelocations
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            if not row['Address']:
                continue

            obj = _createObjectByType("StorageLocation", setup_folder, tmpID())
            obj.edit(
                title=row['Address'],
                SiteTitle=row['SiteTitle'],
                SiteCode=row['SiteCode'],
                SiteDescription=row['SiteDescription'],
                LocationTitle=row['LocationTitle'],
                LocationCode=row['LocationCode'],
                LocationDescription=row['LocationDescription'],
                LocationType=row['LocationType'],
                ShelfTitle=row['ShelfTitle'],
                ShelfCode=row['ShelfCode'],
                ShelfDescription=row['ShelfDescription'],
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Sample_Conditions(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_sampleconditions
        for row in self.get_rows(3):
            if row['title']:
                obj = _createObjectByType("SampleCondition", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    description=row.get('description', '')
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Analysis_Categories(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_analysiscategories
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            department = None
            if row.get('Department_title', None):
                department = self.get_object(bsc, 'Department',
                                             row.get('Department_title'))
            if row.get('title', None) and department:
                obj = _createObjectByType("AnalysisCategory", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''))
                obj.setDepartment(department)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))
            elif not row.get('title', None):
                logger.warning("Error in in " + self.sheetname + ". Missing Title field")
            elif not row.get('Department_title', None):
                logger.warning("Error in " + self.sheetname + ". Department field missing.")
            else:
                logger.warning("Error in " + self.sheetname + ". Department "
                               + row.get('Department_title') + "is wrong.")


class Methods(WorksheetImporter):

    def Import(self):
        folder = self.context.methods
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if row['title']:
                calculation = self.get_object(bsc, 'Calculation', row.get('Calculation_title'))
                obj = _createObjectByType("Method", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''),
                    Instructions=row.get('Instructions', ''),
                    ManualEntryOfResults=row.get('ManualEntryOfResults', True),
                    Calculation=calculation,
                    MethodID=row.get('MethodID', ''),
                    Accredited=row.get('Accredited', True),
                )
                # Obtain all created methods
                catalog = getToolByName(self.context, 'portal_catalog')
                methods_brains = catalog.searchResults({'portal_type': 'Method'})
                # If a the new method has the same MethodID as a created method, remove MethodID value.
                for methods in methods_brains:
                    if methods.getObject().get('MethodID', '') != '' and methods.getObject.get('MethodID', '') == obj['MethodID']:
                        obj.edit(MethodID='')

                if row['MethodDocument']:
                    path = resource_filename(
                        self.dataset_project,
                        "setupdata/%s/%s" % (self.dataset_name,
                                             row['MethodDocument'])
                    )
                    try:
                        file_data = read_file(path)
                        obj.setMethodDocument(file_data)
                    except Exception as msg:
                        logger.warning(msg[0] + " Error on sheet: " + self.sheetname)

                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Sampling_Deviations(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_samplingdeviations
        for row in self.get_rows(3):
            if row['title']:
                obj = _createObjectByType("SamplingDeviation", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    description=row.get('description', '')
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Calculations(WorksheetImporter):

    def get_interim_fields(self):
        # preload Calculation Interim Fields sheet
        sheetname = 'Calculation Interim Fields'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        if not worksheet:
            return
        self.interim_fields = {}
        rows = self.get_rows(3, worksheet=worksheet)
        for row in rows:
            calc_title = row['Calculation_title']
            if calc_title not in self.interim_fields.keys():
                self.interim_fields[calc_title] = []
            self.interim_fields[calc_title].append({
                'keyword': row['keyword'],
                'title': row.get('title', ''),
                'type': 'int',
                'hidden': ('hidden' in row and row['hidden']) and True or False,
                'value': row['value'],
                'unit': row['unit'] and row['unit'] or ''})

    def Import(self):
        self.get_interim_fields()
        folder = self.context.bika_setup.bika_calculations
        for row in self.get_rows(3):
            if not row['title']:
                continue
            calc_title = row['title']
            calc_interims = self.interim_fields.get(calc_title, [])
            formula = row['Formula']
            # scan formula for dep services
            keywords = re.compile(r"\[([^\.^\]]+)\]").findall(formula)
            # remove interims from deps
            interim_keys = [k['keyword'] for k in calc_interims]
            dep_keywords = [k for k in keywords if k not in interim_keys]

            obj = _createObjectByType("Calculation", folder, tmpID())
            obj.edit(
                title=calc_title,
                description=row.get('description', ''),
                InterimFields=calc_interims,
                Formula=str(row['Formula'])
            )
            for kw in dep_keywords:
                self.defer(src_obj=obj,
                           src_field='DependentServices',
                           dest_catalog='bika_setup_catalog',
                           dest_query={'portal_type': 'AnalysisService',
                                       'getKeyword': kw}
                           )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))

        # Now we have the calculations registered, try to assign default calcs
        # to methods
        sheet = self.workbook.get_sheet_by_name("Methods")
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, sheet):
            if row.get('title', '') and row.get('Calculation_title', ''):
                meth = self.get_object(bsc, "Method", row.get('title'))
                if meth and not meth.getCalculation():
                    calctit = safe_unicode(row['Calculation_title']).encode('utf-8')
                    calc = self.get_object(bsc, "Calculation", calctit)
                    if calc:
                        meth.setCalculation(calc.UID())


class Analysis_Services(WorksheetImporter):

    def load_interim_fields(self):
        # preload AnalysisService InterimFields sheet
        sheetname = 'AnalysisService InterimFields'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        if not worksheet:
            return
        self.service_interims = {}
        rows = self.get_rows(3, worksheet=worksheet)
        for row in rows:
            service_title = row['Service_title']
            if service_title not in self.service_interims.keys():
                self.service_interims[service_title] = []
            self.service_interims[service_title].append({
                'keyword': row['keyword'],
                'title': row.get('title', ''),
                'type': 'int',
                'value': row['value'],
                'unit': row['unit'] and row['unit'] or ''})

    def load_result_options(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        sheetname = 'AnalysisService ResultOptions'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        if not worksheet:
            return
        for row in self.get_rows(3, worksheet=worksheet):
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('Service_title'))
            if not service:
                return
            sro = service.getResultOptions()
            sro.append({'ResultValue': row['ResultValue'],
                        'ResultText': row['ResultText']})
            service.setResultOptions(sro)

    def load_service_uncertainties(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        sheetname = 'AnalysisService Uncertainties'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        if not worksheet:
            return

        bucket = {}
        count = 0
        for row in self.get_rows(3, worksheet=worksheet):
            count += 1
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('Service_title'))
            if not service:
                warning = "Unable to load an Analysis Service uncertainty. Service '%s' not found." % row.get('Service_title')
                logger.warning(warning)
                continue
            service_uid = service.UID()
            if service_uid not in bucket:
                bucket[service_uid] = []
            bucket[service_uid].append(
                {'intercept_min': row['Range Min'],
                 'intercept_max': row['Range Max'],
                 'errorvalue': row['Uncertainty Value']}
            )
            if count > 500:
                self.write_bucket(bucket)
                bucket = {}
        if bucket:
            self.write_bucket(bucket)

    def get_methods(self, service_title, default_method):
        """ Return an array of objects of the type Method in accordance to the
            methods listed in the 'AnalysisService Methods' sheet and service
            set in the parameter service_title.
            If default_method is set, it will be included in the returned
            array.
        """
        return self.get_relations(service_title,
                                default_method,
                                'Method',
                                'portal_catalog',
                                'AnalysisService Methods',
                                'Method_title')

    def get_instruments(self, service_title, default_instrument):
        """ Return an array of objects of the type Instrument in accordance to
            the instruments listed in the 'AnalysisService Instruments' sheet
            and service set in the parameter 'service_title'.
            If default_instrument is set, it will be included in the returned
            array.
        """
        return self.get_relations(service_title,
                                default_instrument,
                                'Instrument',
                                'bika_setup_catalog',
                                'AnalysisService Instruments',
                                'Instrument_title')

    def get_relations(self, service_title, default_obj, obj_type, catalog_name, sheet_name, column):
        """ Return an array of objects of the specified type in accordance to
            the object titles defined in the sheet specified in 'sheet_name' and
            service set in the paramenter 'service_title'.
            If a default_obj is set, it will be included in the returned array.
        """
        out_objects = [default_obj] if default_obj else []
        cat = getToolByName(self.context, catalog_name)
        worksheet = self.workbook.get_sheet_by_name(sheet_name)
        if not worksheet:
            return out_objects
        for row in self.get_rows(3, worksheet=worksheet):
            row_as_title = row.get('Service_title')
            if not row_as_title:
                return out_objects
            elif row_as_title != service_title:
                continue
            obj = self.get_object(cat, obj_type, row.get(column))
            if obj:
                if default_obj and default_obj.UID() == obj.UID():
                    continue
                out_objects.append(obj)
        return out_objects

    def write_bucket(self, bucket):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for service_uid, uncertainties in bucket.items():
            obj = bsc(UID=service_uid)[0].getObject()
            _uncert = list(obj.getUncertainties())
            _uncert.extend(uncertainties)
            obj.setUncertainties(_uncert)

    def Import(self):
        self.load_interim_fields()
        folder = self.context.bika_setup.bika_analysisservices
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue

            obj = _createObjectByType("AnalysisService", folder, tmpID())
            MTA = {
                'days': self.to_int(row.get('MaxTimeAllowed_days',0),0),
                'hours': self.to_int(row.get('MaxTimeAllowed_hours',0),0),
                'minutes': self.to_int(row.get('MaxTimeAllowed_minutes',0),0),
            }
            category = self.get_object(bsc, 'AnalysisCategory', row.get('AnalysisCategory_title'))
            department = self.get_object(bsc, 'Department', row.get('Department_title'))
            container = self.get_object(bsc, 'Container', row.get('Container_title'))
            preservation = self.get_object(bsc, 'Preservation', row.get('Preservation_title'))

            # Analysis Service - Method considerations:
            # One Analysis Service can have 0 or n Methods associated (field
            # 'Methods' from the Schema).
            # If the Analysis Service has at least one method associated, then
            # one of those methods can be set as the defualt method (field
            # '_Method' from the Schema).
            #
            # To make it easier, if a DefaultMethod is declared in the
            # Analysis_Services spreadsheet, but the same AS has no method
            # associated in the Analysis_Service_Methods spreadsheet, then make
            # the assumption that the DefaultMethod set in the former has to be
            # associated to the AS although the relation is missing.
            defaultmethod = self.get_object(pc, 'Method', row.get('DefaultMethod_title'))
            methods = self.get_methods(row['title'], defaultmethod)
            if not defaultmethod and methods:
                defaultmethod = methods[0]

            # Analysis Service - Instrument considerations:
            # By default, an Analysis Services will be associated automatically
            # with several Instruments due to the Analysis Service - Methods
            # relation (an Instrument can be assigned to a Method and one Method
            # can have zero or n Instruments associated). There is no need to
            # set this assignment directly, the AnalysisService object will
            # find those instruments.
            # Besides this 'automatic' behavior, an Analysis Service can also
            # have 0 or n Instruments manually associated ('Instruments' field).
            # In this case, the attribute 'AllowInstrumentEntryOfResults' should
            # be set to True.
            #
            # To make it easier, if a DefaultInstrument is declared in the
            # Analysis_Services spreadsheet, but the same AS has no instrument
            # associated in the AnalysisService_Instruments spreadsheet, then
            # make the assumption the DefaultInstrument set in the former has
            # to be associated to the AS although the relation is missing and
            # the option AllowInstrumentEntryOfResults will be set to True.
            defaultinstrument = self.get_object(bsc, 'Instrument', row.get('DefaultInstrument_title'))
            instruments = self.get_instruments(row['title'], defaultinstrument)
            allowinstrentry = True if instruments else False
            if not defaultinstrument and instruments:
                defaultinstrument = instruments[0]

            # The manual entry of results can only be set to false if the value
            # for the attribute "InstrumentEntryOfResults" is False.
            allowmanualentry = True if not allowinstrentry else row.get('ManualEntryOfResults', True)

            # Analysis Service - Calculation considerations:
            # By default, the AnalysisService will use the Calculation associated
            # to the Default Method (the field "UseDefaultCalculation"==True).
            # If the Default Method for this AS doesn't have any Calculation
            # associated and the field "UseDefaultCalculation" is True, no
            # Calculation will be used for this AS ("_Calculation" field is
            # reserved and should not be set directly).
            #
            # To make it easier, if a Calculation is set by default in the
            # spreadsheet, then assume the UseDefaultCalculation has to be set
            # to False.
            deferredcalculation = self.get_object(bsc, 'Calculation', row.get('Calculation_title'))
            usedefaultcalculation = False if deferredcalculation else True
            _calculation = deferredcalculation if deferredcalculation else \
                            (defaultmethod.getCalculation() if defaultmethod else None)

            obj.edit(
                title=row['title'],
                ShortTitle=row.get('ShortTitle', row['title']),
                description=row.get('description', ''),
                Keyword=row['Keyword'],
                PointOfCapture=row['PointOfCapture'].lower(),
                Category=category,
                Department=department,
                AttachmentOption=row.get('Attachment', '')[0].lower() if row.get('Attachment', '') else 'p',
                Unit=row['Unit'] and row['Unit'] or None,
                Precision=row['Precision'] and str(row['Precision']) or '0',
                ExponentialFormatPrecision=str(self.to_int(row.get('ExponentialFormatPrecision',7),7)),
                LowerDetectionLimit='%06f' % self.to_float(row.get('LowerDetectionLimit', '0.0'), 0),
                UpperDetectionLimit='%06f' % self.to_float(row.get('UpperDetectionLimit', '1000000000.0'), 1000000000.0),
                DetectionLimitSelector=self.to_bool(row.get('DetectionLimitSelector',0)),
                MaxTimeAllowed=MTA,
                Price="%02f" % Float(row['Price']),
                BulkPrice="%02f" % Float(row['BulkPrice']),
                VAT="%02f" % Float(row['VAT']),
                _Method=defaultmethod,
                Methods=methods,
                ManualEntryOfResults=allowmanualentry,
                InstrumentEntryOfResults=allowinstrentry,
                Instruments=instruments,
                Calculation=_calculation,
                UseDefaultCalculation=usedefaultcalculation,
                DuplicateVariation="%02f" % Float(row['DuplicateVariation']),
                Accredited=self.to_bool(row['Accredited']),
                InterimFields=hasattr(self, 'service_interims') and self.service_interims.get(
                    row['title'], []) or [],
                Separate=self.to_bool(row.get('Separate', False)),
                Container=container,
                Preservation=preservation,
                CommercialID=row.get('CommercialID', ''),
                ProtocolID=row.get('ProtocolID', '')
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))
        self.load_result_options()
        self.load_service_uncertainties()


class Analysis_Specifications(WorksheetImporter):

    def resolve_service(self, row):
        bsc = getToolByName(self.context, "bika_setup_catalog")
        service = bsc(
            portal_type="AnalysisService",
            title=safe_unicode(row["service"])
        )
        if not service:
            service = bsc(
                portal_type="AnalysisService",
                getKeyword=safe_unicode(row["service"])
            )
        service = service[0].getObject()
        return service

    def Import(self):
        s_t = ""
        bucket = {}
        pc = getToolByName(self.context, "portal_catalog")
        bsc = getToolByName(self.context, "bika_setup_catalog")
        # collect up all values into the bucket
        for row in self.get_rows(3):
            title = row.get("Title", False)
            if not title:
                title = row.get("title", False)
                if not title:
                    continue
            parent = row["Client_title"] if row["Client_title"] else "lab"
            st = row["SampleType_title"] if row["SampleType_title"] else ""
            service = self.resolve_service(row)

            if parent not in bucket:
                bucket[parent] = {}
            if title not in bucket[parent]:
                bucket[parent][title] = {"sampletype": st, "resultsrange": []}
            bucket[parent][title]["resultsrange"].append({
                "keyword": service.getKeyword(),
                "min": row["min"] if row["min"] else "0",
                "max": row["max"] if row["max"] else "0",
            })
        # write objects.
        for parent in bucket.keys():
            for title in bucket[parent]:
                if parent == "lab":
                    folder = self.context.bika_setup.bika_analysisspecs
                else:
                    proxy = pc(portal_type="Client", getName=safe_unicode(parent))[0]
                    folder = proxy.getObject()
                st = bucket[parent][title]["sampletype"]
                resultsrange = bucket[parent][title]["resultsrange"]
                if st:
                    st_uid = bsc(portal_type="SampleType", title=safe_unicode(st))[0].UID
                obj = _createObjectByType("AnalysisSpec", folder, tmpID())
                obj.edit(title=title)
                obj.setResultsRange(resultsrange)
                if st:
                    obj.setSampleType(st_uid)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Analysis_Profiles(WorksheetImporter):

    def load_analysis_profile_services(self):
        sheetname = 'Analysis Profile Services'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        self.profile_services = {}
        if not worksheet:
            return
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, worksheet=worksheet):
            if not row.get('Profile','') or not row.get('Service',''):
                continue
            if row['Profile'] not in self.profile_services.keys():
                self.profile_services[row['Profile']] = []
            # Here we match againts Keyword or Title.
            # XXX We need a utility for this kind of thing.
            service = self.get_object(bsc, 'AnalysisService', row.get('Service'))
            if not service:
                service = bsc(portal_type='AnalysisService',
                              getKeyword=row['Service'])[0].getObject()
            self.profile_services[row['Profile']].append(service)

    def Import(self):
        self.load_analysis_profile_services()
        folder = self.context.bika_setup.bika_analysisprofiles
        for row in self.get_rows(3):
            if row['title']:
                obj = _createObjectByType("AnalysisProfile", folder, tmpID())
                obj.edit(title=row['title'],
                         description=row.get('description', ''),
                         ProfileKey=row['ProfileKey'],
                         CommercialID=row.get('CommercialID', ''),
                         AnalysisProfilePrice="%02f" % Float(row.get('AnalysisProfilePrice', '0.0')),
                         AnalysisProfileVAT="%02f" % Float(row.get('AnalysisProfileVAT', '0.0')),
                         UseAnalysisProfilePrice=row.get('UseAnalysisProfilePrice', False)
                         )
                obj.setService(self.profile_services[row['title']])
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class AR_Templates(WorksheetImporter):

    def load_artemplate_analyses(self):
        sheetname = 'AR Template Analyses'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        self.artemplate_analyses = {}
        if not worksheet:
            return
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, worksheet=worksheet):
            # XXX service_uid is not a uid
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('service_uid'))
            if row['ARTemplate'] not in self.artemplate_analyses.keys():
                self.artemplate_analyses[row['ARTemplate']] = []
            self.artemplate_analyses[row['ARTemplate']].append(
                {'service_uid': service.UID(),
                 'partition': row['partition']
                 }
            )

    def load_artemplate_partitions(self):
        sheetname = 'AR Template Partitions'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        self.artemplate_partitions = {}
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        if not worksheet:
            return
        for row in self.get_rows(3, worksheet=worksheet):
            if row['ARTemplate'] not in self.artemplate_partitions.keys():
                self.artemplate_partitions[row['ARTemplate']] = []
            container = self.get_object(bsc, 'Container',
                                        row.get('container'))
            preservation = self.get_object(bsc, 'Preservation',
                                           row.get('preservation'))
            self.artemplate_partitions[row['ARTemplate']].append({
                'part_id': row['part_id'],
                'Container': container.Title(),
                'container_uid': container.UID(),
                'Preservation': preservation.Title(),
                'preservation_uid': preservation.UID()})

    def Import(self):
        self.load_artemplate_analyses()
        self.load_artemplate_partitions()
        folder = self.context.bika_setup.bika_artemplates
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue
            analyses = self.artemplate_analyses[row['title']]
            client_title = row['Client_title'] or 'lab'
            if row['title'] in self.artemplate_partitions:
                partitions = self.artemplate_partitions[row['title']]
            else:
                partitions = [{'part_id': 'part-1',
                               'container': '',
                               'preservation': ''}]

            if client_title == 'lab':
                folder = self.context.bika_setup.bika_artemplates
            else:
                folder = pc(portal_type='Client',
                            getName=client_title)[0].getObject()

            sampletype = self.get_object(bsc, 'SampleType',
                                         row.get('SampleType_title'))
            samplepoint = self.get_object(bsc, 'SamplePoint',
                                         row.get('SamplePoint_title'))

            obj = _createObjectByType("ARTemplate", folder, tmpID())
            obj.edit(
                title=str(row['title']),
                description=row.get('description', ''),
                Remarks=row.get('Remarks', ''),)
            obj.setSampleType(sampletype)
            obj.setSamplePoint(samplepoint)
            obj.setPartitions(partitions)
            obj.setAnalyses(analyses)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Reference_Definitions(WorksheetImporter):

    def load_reference_definition_results(self):
        sheetname = 'Reference Definition Results'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        if not worksheet:
            sheetname = 'Reference Definition Values'
            worksheet = self.workbook.get_sheet_by_name(sheetname)
            if not worksheet:
                return
        self.results = {}
        if not worksheet:
            return
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, worksheet=worksheet):
            if row['ReferenceDefinition_title'] not in self.results.keys():
                self.results[row['ReferenceDefinition_title']] = []
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('service'))
            self.results[
                row['ReferenceDefinition_title']].append({
                    'uid': service.UID(),
                    'result': row['result'] if row['result'] else '0',
                    'min': row['min'] if row['min'] else '0',
                    'max': row['max'] if row['max'] else '0'})

    def Import(self):
        self.load_reference_definition_results()
        folder = self.context.bika_setup.bika_referencedefinitions
        for row in self.get_rows(3):
            if not row['title']:
                continue
            obj = _createObjectByType("ReferenceDefinition", folder, tmpID())
            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Blank=self.to_bool(row['Blank']),
                ReferenceResults=self.results.get(row['title'], []),
                Hazardous=self.to_bool(row['Hazardous']))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Worksheet_Templates(WorksheetImporter):

    def load_wst_layouts(self):
        sheetname = 'Worksheet Template Layouts'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        self.wst_layouts = {}
        if not worksheet:
            return
        for row in self.get_rows(3, worksheet=worksheet):
            if row['WorksheetTemplate_title'] \
               not in self.wst_layouts.keys():
                self.wst_layouts[
                    row['WorksheetTemplate_title']] = []
            self.wst_layouts[
                row['WorksheetTemplate_title']].append({
                    'pos': row['pos'],
                    'type': row['type'],
                    'blank_ref': row['blank_ref'],
                    'control_ref': row['control_ref'],
                    'dup': row['dup']})

    def load_wst_services(self):
        sheetname = 'Worksheet Template Services'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        self.wst_services = {}
        if not worksheet:
            return
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, worksheet=worksheet):
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('service'))
            if row['WorksheetTemplate_title'] not in self.wst_services.keys():
                self.wst_services[row['WorksheetTemplate_title']] = []
            self.wst_services[
                row['WorksheetTemplate_title']].append(service.UID())

    def Import(self):
        self.load_wst_services()
        self.load_wst_layouts()
        folder = self.context.bika_setup.bika_worksheettemplates
        for row in self.get_rows(3):
            if row['title']:
                obj = _createObjectByType("WorksheetTemplate", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''),
                    Layout=self.wst_layouts[row['title']])
                obj.setService(self.wst_services[row['title']])
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Setup(WorksheetImporter):


    def get_field_value(self, field, value):
        if value is None:
            return None
        converters = {
            "integer": self.to_integer_value,
            "fixedpoint": self.to_fixedpoint_value,
            "boolean": self.to_boolean_value,
            "string": self.to_string_value,
            "reference": self.to_reference_value,
            "duration": self.to_duration_value
        }
        try:
            return converters.get(field.type, None)(field, value)
        except:
            logger.error("No valid type for Setup.{} ({}): {}"
                         .format(field.getName(), field.type, value))

    def to_integer_value(self, field, value):
        return str(int(value))

    def to_fixedpoint_value(self, field, value):
        return str(float(value))

    def to_boolean_value(self, field, value):
        return self.to_bool(value)

    def to_string_value(self, field, value):
        if field.vocabulary:
            return self.to_string_vocab_value(field, value)
        return value and str(value) or ""

    def to_reference_value(self, field, value):
        if not value:
            return None

        brains = api.search({"title": to_unicode(value)})
        if brains:
            return api.get_uid(brains[0])

        msg = "No object found for Setup.{0} ({1}): {2}"
        msg = msg.format(field.getName(), field.type, value)
        logger.error(msg)
        raise ValueError(msg)

    def to_string_vocab_value(self, field, value):
        vocabulary = field.vocabulary
        if type(vocabulary) is str:
            vocabulary = getFromString(api.get_setup(), vocabulary)
        else:
            vocabulary = vocabulary.items()

        if not vocabulary:
            raise ValueError("Empty vocabulary for {}".format(field.getName()))

        if type(vocabulary) in (tuple, list):
            vocabulary = {item[0]: item[1] for item in vocabulary}

        for key, val in vocabulary.items():
            key_low = str(to_utf8(key)).lower()
            val_low = str(to_utf8(val)).lower()
            value_low = str(value).lower()
            if key_low == value_low or val_low == value_low:
                return key
        raise ValueError("Vocabulary entry not found")

    def to_duration_value(self, field, values):
        duration = ["days", "hours", "minutes"]
        duration = map(lambda d: "{}_{}".format(field.getName(), d), duration)
        return dict(
            days=api.to_int(values.get(duration[0], 0), 0),
            hours=api.to_int(values.get(duration[1], 0), 0),
            minutes=api.to_int(values.get(duration[2], 0), 0))

    def Import(self):
        values = {}
        for row in self.get_rows(3):
            values[row['Field']] = row['Value']

        bsetup = self.context.bika_setup
        bschema = bsetup.Schema()
        for field in bschema.fields():
            value = None
            field_name = field.getName()
            if field_name in values:
                value = self.get_field_value(field, values[field_name])
            elif field.type == "duration":
                value = self.get_field_value(field, values)

            if value is None:
                continue
            try:
                obj_field = bsetup.getField(field_name)
                obj_field.set(bsetup, str(value))
            except:
                logger.error("No valid type for Setup.{} ({}): {}"
                             .format(field_name, field.type, value))


class ID_Prefixes(WorksheetImporter):

    def Import(self):
        prefixes = self.context.bika_setup.getIDFormatting()
        for row in self.get_rows(3):
            # remove existing prefix from list
            prefixes = [p for p in prefixes
                        if p['portal_type'] != row['portal_type']]
            # The spreadsheet will contain 'none' for user's visual stuff, but it means 'no separator'
            separator = row.get('separator', '-')
            separator = '' if separator == 'none' else separator
            # add new prefix to list
            prefixes.append({'portal_type': row['portal_type'],
                             'padding': row['padding'],
                             'prefix': row['prefix'],
                             'separator': separator})
        #self.context.bika_setup.setIDFormatting(prefixes)


class Attachment_Types(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_attachmenttypes
        for row in self.get_rows(3):
            obj = _createObjectByType("AttachmentType", folder, tmpID())
            obj.edit(
                title=row['title'],
                description=row.get('description', ''))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Reference_Samples(WorksheetImporter):

    def load_reference_sample_results(self, sample):
        sheetname = 'Reference Sample Results'
        if not hasattr(self, 'results_worksheet'):
            worksheet = self.workbook.get_sheet_by_name(sheetname)
            if not worksheet:
                return
            self.results_worksheet = worksheet
        results = []
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, worksheet=self.results_worksheet):
            if row['ReferenceSample_id'] != sample.getId():
                continue
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('AnalysisService_title'))
            if not service:
                warning = "Unable to load a reference sample result. Service %s not found."
                logger.warning(warning, sheetname)
                continue
            results.append({
                    'uid': service.UID(),
                    'result': row['result'],
                    'min': row['min'],
                    'max': row['max']})
        sample.setReferenceResults(results)

    def load_reference_analyses(self, sample):
        sheetname = 'Reference Analyses'
        if not hasattr(self, 'analyses_worksheet'):
            worksheet = self.workbook.get_sheet_by_name(sheetname)
            if not worksheet:
                return
            self.analyses_worksheet = worksheet
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, worksheet=self.analyses_worksheet):
            if row['ReferenceSample_id'] != sample.getId():
                continue
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('AnalysisService_title'))
            # Analyses are keyed/named by service keyword
            obj = _createObjectByType("ReferenceAnalysis", sample, row['id'])
            obj.edit(title=row['id'],
                     ReferenceType=row['ReferenceType'],
                     Result=row['Result'],
                     Analyst=row['Analyst'],
                     Instrument=row['Instrument'],
                     Retested=row['Retested']
                     )
            obj.setService(service)
            # obj.setCreators(row['creator'])
            # obj.setCreationDate(row['created'])
            # self.set_wf_history(obj, row['workflow_history'])
            obj.unmarkCreationFlag()

            self.load_reference_analysis_interims(obj)

    def load_reference_analysis_interims(self, analysis):
        sheetname = 'Reference Analysis Interims'
        if not hasattr(self, 'interim_worksheet'):
            worksheet = self.workbook.get_sheet_by_name(sheetname)
            if not worksheet:
                return
            self.interim_worksheet = worksheet
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        interims = []
        for row in self.get_rows(3, worksheet=self.interim_worksheet):
            if row['ReferenceAnalysis_id'] != analysis.getId():
                continue
            interims.append({
                    'keyword': row['keyword'],
                    'title': row['title'],
                    'value': row['value'],
                    'unit': row['unit'],
                    'hidden': row['hidden']})
        analysis.setInterimFields(interims)

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['id']:
                continue
            supplier = bsc(portal_type='Supplier',
                           getName=row.get('Supplier_title', ''))[0].getObject()
            obj = _createObjectByType("ReferenceSample", supplier, row['id'])
            ref_def = self.get_object(bsc, 'ReferenceDefinition',
                                      row.get('ReferenceDefinition_title'))
            ref_man = self.get_object(bsc, 'Manufacturer',
                                      row.get('Manufacturer_title'))
            obj.edit(title=row['id'],
                     description=row.get('description', ''),
                     Blank=self.to_bool(row['Blank']),
                     Hazardous=self.to_bool(row['Hazardous']),
                     CatalogueNumber=row['CatalogueNumber'],
                     LotNumber=row['LotNumber'],
                     Remarks=row['Remarks'],
                     ExpiryDate=row['ExpiryDate'],
                     DateSampled=row['DateSampled'],
                     DateReceived=row['DateReceived'],
                     DateOpened=row['DateOpened'],
                     DateExpired=row['DateExpired'],
                     DateDisposed=row['DateDisposed']
                     )
            obj.setReferenceDefinition(ref_def)
            obj.setManufacturer(ref_man)
            obj.unmarkCreationFlag()

            self.load_reference_sample_results(obj)
            self.load_reference_analyses(obj)

class Analysis_Requests(WorksheetImporter):

    def load_analyses(self, sample):
        sheetname = 'Analyses'
        if not hasattr(self, 'analyses_worksheet'):
            worksheet = self.workbook.get_sheet_by_name(sheetname)
            if not worksheet:
                return
            self.analyses_worksheet = worksheet
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        bc = getToolByName(self.context, 'bika_catalog')
        for row in self.get_rows(3, worksheet=self.analyses_worksheet):
            service = bsc(portal_type='AnalysisService',
                          title=row['AnalysisService_title'])[0].getObject()
            # analyses are keyed/named by keyword
            ar = bc(portal_type='AnalysisRequest', id=row['AnalysisRequest_id'])[0].getObject()
            obj = create_analysis(
                ar, service,
                Result=row['Result'],
                ResultCaptureDate=row['ResultCaptureDate'],
                Analyst=row['Analyst'],
                Instrument=row['Instrument'],
                Retested=self.to_bool(row['Retested']),
                MaxTimeAllowed={
                    'days': int(row.get('MaxTimeAllowed_days', 0)),
                    'hours': int(row.get('MaxTimeAllowed_hours', 0)),
                    'minutes': int(row.get('MaxTimeAllowed_minutes', 0)),
                },
            )

            analyses = ar.objectValues('Analyses')
            analyses = list(analyses)
            analyses.append(obj)
            ar.setAnalyses(analyses)
            obj.unmarkCreationFlag()

            self.load_analysis_interims(obj)

    def load_analysis_interims(self, analysis):
        sheetname = 'Reference Analysis Interims'
        if not hasattr(self, 'interim_worksheet'):
            worksheet = self.workbook.get_sheet_by_name(sheetname)
            if not worksheet:
                return
            self.interim_worksheet = worksheet
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        interims = []
        for row in self.get_rows(3, worksheet=self.interim_worksheet):
            if row['ReferenceAnalysis_id'] != analysis.getId():
                continue
            interims.append({
                    'keyword': row['keyword'],
                    'title': row['title'],
                    'value': row['value'],
                    'unit': row['unit'],
                    'hidden': row['hidden']})
        analysis.setInterimFields(interims)

    def Import(self):
        bc = getToolByName(self.context, 'bika_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            if not row['id']:
                continue
            client = pc(portal_type="Client",
                        getName=row['Client_title'])[0].getObject()
            obj = _createObjectByType("AnalysisRequest", client, row['id'])
            contact = pc(portal_type="Contact",
                         getFullname=row['Contact_Fullname'])[0].getObject()
            obj.edit(
                RequestID=row['id'],
                Contact=contact,
                CCEmails=row['CCEmails'],
                ClientOrderNumber=row['ClientOrderNumber'],
                InvoiceExclude=row['InvoiceExclude'],
                DateReceived=row['DateReceived'],
                DatePublished=row['DatePublished'],
                Remarks=row['Remarks']
            )
            if row['CCContact_Fullname']:
                contact = pc(portal_type="Contact",
                             getFullname=row['CCContact_Fullname'])[0].getObject()
                obj.setCCContact(contact)
            if row['AnalysisProfile_title']:
                profile = pc(portal_type="AnalysisProfile",
                             title=row['AnalysisProfile_title'].getObject())
                obj.setProfile(profile)
            if row['ARTemplate_title']:
                template = pc(portal_type="ARTemplate",
                             title=row['ARTemplate_title'])[0].getObject()
                obj.setProfile(template)

            obj.unmarkCreationFlag()

            self.load_analyses(obj)


class Invoice_Batches(WorksheetImporter):

    def Import(self):
        folder = self.context.invoices
        for row in self.get_rows(3):
            obj = _createObjectByType("InvoiceBatch", folder, tmpID())
            if not row['title']:
                message = _("InvoiceBatch has no Title")
                raise Exception(t(message))
            if not row['start']:
                message = _("InvoiceBatch has no Start Date")
                raise Exception(t(message))
            if not row['end']:
                message = _("InvoiceBatch has no End Date")
                raise Exception(t(message))
            obj.edit(
                title=row['title'],
                BatchStartDate=row['start'],
                BatchEndDate=row['end'],
            )
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))
