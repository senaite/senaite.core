from bika.lims.exportimport.dataimport import SetupDataSetList as SDL
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import ISetupDataSetList
from Products.CMFPlone.utils import safe_unicode
from bika.lims.utils import tmpID
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from zope.interface import implements
from pkg_resources import resource_filename

import re
import transaction


class SetupDataSetList(SDL):

    implements(ISetupDataSetList)

    def __call__(self):
        return SDL.__call__(self, projectname="bika.wine")


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
            self.Import()
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
                new_row.append(value)
            row = dict(zip(headers, new_row))

            # parse out addresses
            for add_type in ['Physical', 'Postal', 'Billing']:
                row[add_type] = {}
                if add_type + "_Address" in row:
                    for key in ['Address', 'City', 'State', 'Zip', 'Country']:
                        row[add_type][key] = row["%s_%s" % (add_type, key)]

            yield row

    def get_file_data(self, filename):
        if filename:
            path = resource_filename(
                self.dataset_project,
                "setupdata/%s/%s" % (self.dataset_name, filename))
            file_data = open(path, "rb").read()
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
            for key in ['Address', 'City', 'State', 'Zip', 'Country']:
                addresses[add_type][key.lower()] = row.get("%s_%s" % (add_type, key), '')

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
        if hasattr(obj, 'setEmailAddress'):
            obj.setEmailAddress(row.get('EmailAddress', ''))
        if hasattr(obj, 'setPhone'):
            obj.setPhone(row.get('Phone', ''))
        if hasattr(obj, 'setFax'):
            obj.setFax(row.get('Fax', ''))
        if hasattr(obj, 'setBusinessPhone'):
            obj.setBusinessPhone(row.get('BusinessPhone', ''))
        if hasattr(obj, 'setBusinessFax'):
            obj.setBusinessFax(row.get('BusinessFax', ''))
        if hasattr(obj, 'setHomePhone'):
            obj.setHomePhone(row.get('HomePhone', ''))
        if hasattr(obj, 'setMobilePhone'):
            obj.setMobilePhone(row.get('MobilePhone', ''))


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
            file_data = open(path, "rb").read()
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

        for row in self.get_rows(3):

            # Create LabContact

            if not row['Firstname']:
                continue

            _id = folder.invokeFactory('LabContact', id=tmpID())
            obj = folder[_id]
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            Fullname = row['Firstname'] + " " + row.get('Surname', '')
            obj.edit(
                title=Fullname,
                Salutation=row.get('Salutation', ''),
                Firstname=row['Firstname'],
                Surname=row.get('Surname', ''),
                JobTitle=row.get('JobTitle', ''),
                Username=row.get('Username', ''),
                Signature=self.get_file_data(row.get('Signature', None))
            )
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

            if(row['Username']):
                member = portal_registration.addMember(
                    row['Username'],
                    row['Password'],
                    properties={
                        'username': row['Username'],
                        'email': row['EmailAddress'],
                        'fullname': Fullname}
                )
                groups = row.get('Groups', '')
                if groups:
                    group_ids = [g.strip() for g in groups.split(',')]
                    # Add user to all specified groups
                    for group_id in group_ids:
                        group = portal_groups.getGroupById(group_id)
                        if group:
                            group.addMember(row['Username'])
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
                        row['Username'], ['Owner', ])


class Lab_Departments(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_departments
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        lab_contacts = [o.getObject() for o in bsc(portal_type="LabContact")]
        for row in self.get_rows(3):
            if row['title']:
                _id = folder.invokeFactory('Department', id=tmpID())
                obj = folder[_id]
                obj.edit(title=row['title'],
                         description=row.get('description', ''))
                manager = None
                for contact in lab_contacts:
                    if contact.getUsername() == row['LabContact_Username']:
                        manager = contact
                        break
                else:
                    message = "Department: lookup of '%s' in LabContacts/Username failed." % row[
                        'LabContact_Username']
                    logger.info(message)
                if manager:
                    obj.setManager(manager.UID())
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Clients(WorksheetImporter):

    def Import(self):
        folder = self.context.clients
        for row in self.get_rows(3):
            _id = folder.invokeFactory('Client', id=tmpID())
            obj = folder[_id]
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


class Client_Contacts(WorksheetImporter):

    def Import(self):
        portal_groups = getToolByName(self.context, 'portal_groups')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            client = pc(portal_type="Client",
                        Title=row['Client_title'])
            if len(client) == 0:
                raise IndexError("Client invalid: '%s'" % row['Client_title'])
            client = client[0].getObject()
            _id = client.invokeFactory('Contact', id=tmpID())
            contact = client[_id]
            fullname = "%(Firstname)s %(Surname)s" % row
            pub_pref = [x.strip() for x in
                        row.get('PublicationPreference', '').split(",")]
            contact.edit(
                Salutation=row.get('Salutation', ''),
                Firstname=row.get('Firstname', ''),
                Surname=row.get('Surname', ''),
                Username=row.get('Username', ''),
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

            # Create Plone user
            username = safe_unicode(row['Username']).decode('utf-8')
            password = safe_unicode(row['Password']).decode('utf-8')
            if(username):
                try:
                    self.portal_registration.addMember(
                        username,
                        password,
                        properties={
                            'username': row['Username'],
                            'email': row['EmailAddress'],
                            'fullname': fullname}
                    )
                except:
                    logger.info("Error adding user (already exists?): %s" %
                                username)
                contact.aq_parent.manage_setLocalRoles(username,
                                                       ['Owner', ])

                # add user to Clients group
                group = portal_groups.getGroupById('Clients')
                group.addMember(username)


class Container_Types(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_containertypes
        for row in self.get_rows(3):
            if not row['title']:
                continue
            _id = folder.invokeFactory('ContainerType', id=tmpID())
            obj = folder[_id]
            obj.edit(title=row['title'],
                     description=row.get('description', ''))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Preservations(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_preservations
        for row in self.get_rows(3):
            if not row['title']:
                continue
            _id = folder.invokeFactory('Preservation', id=tmpID())
            obj = folder[_id]
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


class Containers(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_containers
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue
            _id = folder.invokeFactory('Container', id=tmpID())
            obj = folder[_id]
            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Capacity=row.get('Capacity', 0),
                PrePreserved=self.to_bool(row['PrePreserved'])
            )
            if row['ContainerType_title']:
                ct = bsc(portal_type='ContainerType',
                         title=row['ContainerType_title'])
                if ct:
                    obj.setContainerType(ct[0].getObject())
            if row['Preservation_title']:
                pres = bsc(portal_type='Preservation',
                           title=row['Preservation_title'])
                if pres:
                    obj.setPreservation(pres[0].getObject())
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Suppliers(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_suppliers
        for row in self.get_rows(3):
            _id = folder.invokeFactory('Supplier', id=tmpID())
            obj = folder[_id]
            if row['Name']:
                obj.edit(
                    Name=row.get('Name', ''),
                    TaxNumber=row.get('TaxNumber', ''),
                    AccountType=row.get('AccountType', {}),
                    AccountName=row.get('AccountName', {}),
                    AccountNumber=row.get('AccountNumber', ''),
                    BankName=row.get('BankName', ''),
                    BankBranch=row.get('BankBranch', ''),
                )
                self.fill_contactfields(row, obj)
                self.fill_addressfields(row, obj)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


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
            _id = folder.invokeFactory('SupplierContact', id=tmpID())
            obj = folder[_id]
            obj.edit(
                Firstname=row['Firstname'],
                Surname=row.get('Surname', ''),
                Username=row.get('Username')
            )
            self.fill_contactfields(row, obj)
            self.fill_addressfields(row, obj)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Manufacturers(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_manufacturers
        for row in self.get_rows(3):
            _id = folder.invokeFactory('Manufacturer', id=tmpID())
            obj = folder[_id]
            if row['title']:
                obj.edit(
                    title=row['title'],
                    description=row.get('description', '')
                )
                self.fill_addressfields(row, obj)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Instrument_Types(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_instrumenttypes
        for row in self.get_rows(3):
                _id = folder.invokeFactory('InstrumentType', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''))
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Instruments(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_instruments
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if (not row['Type']
               or not row['title']
               or not row['Supplier']
               or not row['Brand']):
                continue

            _id = folder.invokeFactory('Instrument', id=tmpID())
            obj = folder[_id]

            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Type=row['Type'],
                Brand=row['Brand'],
                Model=row['Model'],
                SerialNo=row.get('SerialNo', ''),
                CalibrationCertificate=row.get('CalibrationCertificate', ''),
                CalibrationExpiryDate=row.get('CalibrationExpiryDate', ''),
                DataInterface=row.get('DataInterface', '')
            )

            instrumenttype = bsc(portal_type='InstrumentType',
                                 title=row['Type'])[0].getObject() \
                if row.get('Type', '') else None
            obj.setInstrumentType(instrumenttype)
            manufacturer = bsc(portal_type='Manufacturer',
                               title=row['Brand'])[0].getObject() \
                if row.get('Brand', '') else None
            obj.setManufacturer(manufacturer)
            supplier = bsc(portal_type='Supplier',
                           getName=row['Supplier'])[0].getObject() \
                if row.get('Supplier', '') else None
            obj.setSupplier(supplier)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Instrument_Validations(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['instrument'] or not row['title']:
                continue

            folder = bsc(portal_type='Instrument', title=row['instrument'])
            if folder:
                folder = folder[0].getObject()
                _id = folder.invokeFactory('InstrumentValidation', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=row['title'],
                    DownFrom=row.get('downfrom', ''),
                    DownTo=row.get('downto', ''),
                    Validator=row.get('validator', ''),
                    Considerations=row.get('considerations', ''),
                    WorkPerformed=row.get('workperformed', ''),
                    Remarks=row.get('remarks', '')
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Instrument_Calibrations(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['instrument'] or not row['title']:
                continue

            folder = bsc(portal_type='Instrument', title=row['instrument'])
            if folder:
                folder = folder[0].getObject()
                _id = folder.invokeFactory('InstrumentCalibration', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=row['title'],
                    DownFrom=row.get('downfrom', ''),
                    DownTo=row.get('downto', ''),
                    Calibrator=row.get('calibrator', ''),
                    Considerations=row.get('considerations', ''),
                    WorkPerformed=row.get('workperformed', ''),
                    Remarks=row.get('remarks', '')
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Instrument_Certifications(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['instrument'] or not row['title']:
                continue

            folder = bsc(portal_type='Instrument', title=row['instrument'])
            if folder:
                folder = folder[0].getObject()
                _id = folder.invokeFactory(
                    'InstrumentCertification', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=row['title'],
                    Date=row.get('date', ''),
                    ValidFrom=row.get('validfrom', ''),
                    ValidTo=row.get('validto', ''),
                    Agency=row.get('agency', ''),
                    Remarks=row.get('remarks', '')
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Instrument_Maintenance_Tasks(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['instrument'] or not row['title'] or not row['type']:
                continue

            folder = bsc(portal_type='Instrument', title=row['instrument'])
            if folder:
                folder = folder[0].getObject()
                _id = folder.invokeFactory('InstrumentMaintenanceTask',
                                           id=tmpID())
                obj = folder[_id]
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


class Instrument_Schedule(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['instrument'] or not row['title'] or not row['type']:
                continue
            folder = bsc(portal_type='Instrument', title=row['instrument'])
            if folder:
                folder = folder[0].getObject()
                _id = folder.invokeFactory('InstrumentScheduledTask',
                                           id=tmpID())
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
                obj = folder[_id]
                obj.edit(
                    title=row['title'],
                    Type=row['type'],
                    ScheduleCriteria=criteria,
                    Considerations=row.get('considerations', ''),
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Sample_Matrices(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_samplematrices
        for row in self.get_rows(3):
            if not row['title']:
                continue
            _id = folder.invokeFactory('SampleMatrix', id=tmpID())
            obj = folder[_id]
            obj.edit(
                title=row['title'],
                description=row.get('description', '')
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Batch_Labels(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_batchlabels
        for row in self.get_rows(3):
            if row['title']:
                _id = folder.invokeFactory('BatchLabel', id=tmpID())
                obj = folder[_id]
                obj.edit(title=row['title'])
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Sample_Types(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_sampletypes
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue
            _id = folder.invokeFactory('SampleType', id=tmpID())
            obj = folder[_id]
            samplematrix = bsc(portal_type='SampleMatrix',
                               title=row['SampleMatrix_title'])[0].getObject() \
                if row.get('SampleMatrix_title', '') else None
            containertype = bsc(portal_type='ContainerType',
                                title=row['ContainerType_title'])[0].getObject() \
                if row.get('ContainerType_title', '') else None
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
            samplepoint = bsc(portal_type='SamplePoint',
                              title=row['SamplePoint_title']) \
                if row.get('SamplePoint_title', '') else None
            samplepoint = samplepoint[0].getObject() \
                if samplepoint else None
            if samplepoint:
                obj.setSamplePoints([samplepoint, ])
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Sample_Points(WorksheetImporter):

    def Import(self):
        setup_folder = self.context.bika_setup.bika_samplepoints
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue
            if row['Client_title']:
                client_title = row['Client_title']
                client = self.portal_catalog(portal_type="Client",
                                             Title=client_title)
                if len(client) == 0:
                    raise IndexError("Sample Point %s: Client invalid: '%s'" %
                                     (row['title'], client_title))
                folder = client[0].getObject()
            else:
                folder = setup_folder

            if row['Latitude']:
                logger.log("Ignored SamplePoint Latitude", 'error')
            if row['Longitude']:
                logger.log("Ignored SamplePoint Longitude", 'error')

            _id = folder.invokeFactory('SamplePoint', id=tmpID())
            obj = folder[_id]
            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Composite=self.to_bool(row['Composite']),
                Elevation=row['Elevation'],
            )
            sampletype = bsc(portal_type='SampleType',
                             title=row['SampleType_title']) \
                if row.get('SampleType_title', '') else None
            sampletype = sampletype[0].getObject() \
                if sampletype else None
            if sampletype:
                obj.setSampleTypes([sampletype, ])
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Sample_Point_Sample_Types(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            sampletype = bsc(portal_type='SampleType',
                             title=row['SampleType_title'])
            sampletype = sampletype[0].getObject() if sampletype else None
            samplepoint = bsc(portal_type='SamplePoint',
                              title=row['SamplePoint_title'])
            samplepoint = samplepoint[0].getObject() if samplepoint else None

            sampletypes = samplepoint.getSampleTypes()
            if sampletype not in sampletypes:
                sampletypes.append(sampletype)
                samplepoint.setSampleTypes(sampletypes)

            samplepoints = sampletype.getSamplePoints()
            if samplepoint not in samplepoints:
                samplepoints.append(samplepoint)
                sampletype.setSamplePoints(samplepoints)


class Sample_Conditions(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_sampleconditions
        for row in self.get_rows(3):
            if row['Title']:
                _id = folder.invokeFactory('SampleCondition', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=row['Title'],
                    description=row.get('Description', '')
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Analysis_Categories(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_analysiscategories
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if row['title']:
                _id = folder.invokeFactory('AnalysisCategory', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''))
                if row['Department_title']:
                    department = bsc(portal_type='Department',
                                     title=row['Department_title'])[0].UID
                    obj.setDepartment(department)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Methods(WorksheetImporter):

    def Import(self):
        folder = self.context.methods
        for row in self.get_rows(3):
            if row['title']:
                _id = folder.invokeFactory('Method', id=tmpID())
                obj = folder[_id]

                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''),
                    Instructions=row.get('Instructions', ''))

                if row['MethodDocument']:
                    path = resource_filename(
                        self.dataset_project,
                        "setupdata/%s/%s" % (self.dataset_name,
                                             row['MethodDocument'])
                    )
                    file_data = open(path, "rb").read()
                    obj.setMethodDocument(file_data)

                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Sampling_Deviations(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_samplingdeviations
        for row in self.get_rows(3):
            if row['title']:
                _id = folder.invokeFactory('SamplingDeviation', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=row['title'],
                    description=row.get('description', '')
                )
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Reference_Manufacturers(Manufacturers):

    """BBB
    """


class Reference_Suppliers(Suppliers):

    """BBB
    """


class Reference_Supplier_Contacts(Supplier_Contacts):

    """BBB
    """


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
            keywords = re.compile(r"\[([^\]]+)\]").findall(formula)
            # remove interims from deps
            interim_keys = [k['keyword'] for k in calc_interims]
            dep_keywords = [k for k in keywords if k not in interim_keys]

            _id = folder.invokeFactory('Calculation', id=tmpID())
            obj = folder[_id]
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
            service = bsc(portal_type='AnalysisService',
                          title=row['Service_title'])[0].getObject()
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
            service = bsc(portal_type='AnalysisService',
                          title=row['Service_title'])[0].getObject()
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

    def write_bucket(self, bucket):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for service_uid, uncertainties in bucket.items():
            obj = bsc(UID=service_uid)
            _uncert = list(obj.getUncertainties())
            _uncert.extend(uncertainties)
            obj.setUncertainties(_uncert)

    def Import(self):
        self.load_interim_fields()
        folder = self.context.bika_setup.bika_analysisservices
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue

            _id = folder.invokeFactory('AnalysisService', id=tmpID())
            obj = folder[_id]
            MTA = {
                'days': int(row['MaxTimeAllowed_days'] and row['MaxTimeAllowed_days'] or 0),
                'hours': int(row['MaxTimeAllowed_hours'] and row['MaxTimeAllowed_hours'] or 0),
                'minutes': int(row['MaxTimeAllowed_minutes'] and row['MaxTimeAllowed_minutes'] or 0),
            }
            category = bsc(
                portal_type='AnalysisCategory',
                title=row.get('AnalysisCategory_title', ''))[0].getObject() \
                if row.get('AnalysisCategory_title', '') \
                else None
            department = bsc(
                portal_type='Department',
                title=row.get('Department_title', ''))[0].getObject() \
                if row.get('Department_title', '') \
                else None
            method = bsc(
                portal_type='Method',
                title=row.get('Method', ''))[0].getObject() \
                if row.get('Method', '') \
                else None
            instrument = bsc(
                portal_type='Instrument',
                title=row.get('Instrument_title', ''))[0].getObject() \
                if row.get('Instrument_title', '') \
                else None
            calculation = bsc(
                portal_type='Calculation',
                title=row.get('Calculation_title', ''))[0].getObject() \
                if row.get('Calculation_title', '') \
                else None
            container = bsc(
                portal_type='Container',
                title=row.get('Container_title', ''))[0].getObject() \
                if row.get('Container_title', '') \
                else None
            preservation = bsc(
                portal_type='Preservation',
                title=row.get('Preservation_title', ''))[0].getObject() \
                if row.get('Preservation_title', '') \
                else None

            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Keyword=row['Keyword'],
                PointOfCapture=row['PointOfCapture'],
                Category=category,
                Department=department,
                ReportDryMatter=self.to_bool(row['ReportDryMatter']),
                AttachmentOption=row['Attachment'][0].lower(),
                Unit=row['Unit'] and row['Unit'] or None,
                Precision=row['Precision'] and str(row['Precision']) or '0',
                MaxTimeAllowed=MTA,
                Price=row['Price'] and "%02f" % (
                    float(row['Price'])) or "0,00",
                BulkPrice=row['BulkPrice'] and "%02f" % (
                    float(row['BulkPrice'])) or "0.00",
                VAT=row['VAT'] and "%02f" % (float(row['VAT'])) or "0.00",
                Method=method,
                Instrument=instrument,
                Calculation=calculation,
                DuplicateVariation="%02f" % float(row['DuplicateVariation']),
                Accredited=self.to_bool(row['Accredited']),
                InterimFields=hasattr(self, 'service_interims') and self.service_interims.get(
                    row['title'], []) or [],
                Separate=self.to_bool(row.get('Separate', False)),
                Container=container,
                Preservation=preservation
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
        self.load_result_options()
        self.load_service_uncertainties()


class Analysis_Specifications(WorksheetImporter):

    def Import(self):
        s_t = ''
        c_t = 'lab'
        bucket = {}
        pc = getToolByName(self.context, 'portal_catalog')
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        # collect up all values into the bucket
        for row in self.get_rows(3):
            c_t = row['Client_title'] if row['Client_title'] else 'lab'
            if c_t not in bucket:
                bucket[c_t] = {}
            s_t = row['SampleType_title'] if row['SampleType_title'] else s_t
            if s_t not in bucket[c_t]:
                bucket[c_t][s_t] = []
            service = bsc(portal_type='AnalysisService', title=row['service'])
            if not service:
                service = bsc(portal_type='AnalysisService',
                              getKeyword=row['service'])
            service = service[0].getObject()
            bucket[c_t][s_t].append({
                'keyword': service.getKeyword(),
                'min': row['min'] if row['min'] else '0',
                'max': row['max'] if row['max'] else '0',
                'error': row['error'] if row['error'] else '0'
            })
        # write objects.
        for c_t in bucket:
            if c_t == 'lab':
                folder = self.context.bika_setup.bika_analysisspecs
            else:
                folder = pc(portal_type='Client', title=c_t)[0].getObject()
            for s_t in bucket[c_t]:
                resultsrange = bucket[c_t][s_t]
                sampletype = bsc(portal_type='SampleType', title=s_t)[0]
                _id = folder.invokeFactory('AnalysisSpec', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=sampletype.Title,
                    ResultsRange=resultsrange)
                obj.setSampleType(sampletype.UID)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Analysis_Profiles(WorksheetImporter):

    def load_analysis_profile_services(self):
        sheetname = 'Analysis Profile Services'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        self.profile_services = {}
        if not worksheet:
            return
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, worksheet=worksheet):
            if row['Profile'] not in self.profile_services.keys():
                self.profile_services[row['Profile']] = []
            # Here we match againts Keyword or Title.
            # XXX We need a utility for this kind of thing.
            service = bsc(portal_type='AnalysisService',
                          title=row['Service'])
            if not service:
                service = bsc(portal_type='AnalysisService',
                              getKeyword=row['Service'])
            service = service[0].getObject()
            self.profile_services[row['Profile']].append(service)

    def Import(self):
        self.load_analysis_profile_services()
        folder = self.context.bika_setup.bika_analysisprofiles
        for row in self.get_rows(3):
            if row['title']:
                _id = folder.invokeFactory('AnalysisProfile', id=tmpID())
                obj = folder[_id]
                obj.edit(title=row['title'],
                         description=row.get('description', ''),
                         ProfileKey=row['ProfileKey'])
                obj.setService(self.profile_services[row['title']])
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


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
            service = bsc(portal_type='AnalysisService',
                          title=row.get('service_uid'))[0].getObject()
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
            container = bsc(portal_type='Container',
                            title=row['container']) \
                if row['container'] else []
            preservation = bsc(portal_type='Preservation',
                               title=row['preservation']) \
                if row['preservation'] else []
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
                            title=client_title)[0].getObject()

            sampletype = bsc(portal_type='SampleType',
                             title=row['SampleType_title'])
            sampletype = sampletype[0].getObject() if sampletype else None
            samplepoint = bsc(portal_type='SamplePoint',
                              title=row['SamplePoint_title'])
            samplepoint = samplepoint[0].getObject() if samplepoint else None

            _id = folder.invokeFactory('ARTemplate', id=tmpID())
            obj = folder[_id]
            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Remarks=row.get('Remarks', ''),
                ReportDryMatter=bool(row['ReportDryMatter']))
            obj.setSampleType(sampletype)
            obj.setSamplePoint(samplepoint)
            obj.setPartitions(partitions)
            obj.setAnalyses(analyses)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Reference_Definitions(WorksheetImporter):

    def load_reference_definition_results(self):
        sheetname = 'Reference Definition Results'
        worksheet = self.workbook.get_sheet_by_name(sheetname)
        self.results = {}
        if not worksheet:
            return
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        for row in self.get_rows(3, worksheet=worksheet):
            if row['ReferenceDefinition_title'] not in self.results.keys():
                self.results[row['ReferenceDefinition_title']] = []
            service = bsc(portal_type='AnalysisService',
                          title=row['service'])[0].getObject()
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
            _id = folder.invokeFactory('ReferenceDefinition', id=tmpID())
            obj = folder[_id]
            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Blank=self.to_bool(row['Blank']),
                ReferenceResults=self.results.get(row['title'], []),
                Hazardous=self.to_bool(row['Hazardous']))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


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
            service = bsc(portal_type='AnalysisService',
                          title=row['service'])[0].getObject()
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
                _id = folder.invokeFactory('WorksheetTemplate', id=tmpID())
                obj = folder[_id]
                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''),
                    Layout=self.wst_layouts[row['title']])
                obj.setService(self.wst_services[row['title']])
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)


class Setup(WorksheetImporter):

    def Import(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        values = {}
        for row in self.get_rows(3):
            values[row['Field']] = row['Value']

        DSL = {
            'days': int(values['DefaultSampleLifetime_days'] and values['DefaultSampleLifetime_days'] or 0),
            'hours': int(values['DefaultSampleLifetime_hours'] and values['DefaultSampleLifetime_hours'] or 0),
            'minutes': int(values['DefaultSampleLifetime_minutes'] and values['DefaultSampleLifetime_minutes'] or 0),
        }
        dry_service = bsc(portal_type='AnalysisService',
                          title=values['DryMatterService']) \
            if values.get('DryMatterService', None) else None
        dry_uid = dry_service[0].UID if dry_service else None
        if not dry_uid:
            print "DryMatter service does not exist {0}".format(
                values['DryMatterService'])
        self.context.bika_setup.edit(
            PasswordLifetime=int(values['PasswordLifetime']),
            AutoLogOff=int(values['AutoLogOff']),
            ShowPricing=values.get('ShowPricing', True),
            Currency=values['Currency'],
            MemberDiscount=str(float(values['MemberDiscount'])),
            VAT=str(float(values['VAT'])),
            MinimumResults=int(values['MinimumResults']),
            BatchEmail=int(values['BatchEmail']),
            SamplingWorkflowEnabled=values['SamplingWorkflowEnabled'],
            CategoriseAnalysisServices=self.to_bool(
                values['CategoriseAnalysisServices']),
            EnableAnalysisRemarks=self.to_bool(
                values.get('EnableAnalysisRemarks', '')),
            DryMatterService=dry_uid,
            ARImportOption=values['ARImportOption'],
            ARAttachmentOption=values['ARAttachmentOption'][0].lower(),
            AnalysisAttachmentOption=values[
                'AnalysisAttachmentOption'][0].lower(),
            DefaultSampleLifetime=DSL,
            AutoPrintLabels=values['AutoPrintLabels'].lower(),
            AutoLabelSize=values['AutoLabelSize'].lower(),
            YearInPrefix=self.to_bool(values['YearInPrefix']),
            SampleIDPadding=int(values['SampleIDPadding']),
            ARIDPadding=int(values['ARIDPadding']),
            ExternalIDServer=self.to_bool(values['ExternalIDServer']),
            IDServerURL=values['IDServerURL'],
        )


class ID_Prefixes(WorksheetImporter):

    def Import(self):
        prefixes = self.context.bika_setup.getPrefixes()
        for row in self.get_rows(3):
            # remove existing prefix from list
            prefixes = [p for p in prefixes
                        if p['portal_type'] != row['portal_type']]
            # add new prefix to list
            prefixes.append({'portal_type': row['portal_type'],
                             'padding': row['padding'],
                             'prefix': row['prefix']})
        self.context.bika_setup.setPrefixes(prefixes)


class Attachment_Types(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_attachmenttypes
        for row in self.get_rows(3):
            _id = folder.invokeFactory('AttachmentType', id=tmpID())
            obj = folder[_id]
            obj.edit(
                title=row['title'],
                description=row.get('description', ''))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
