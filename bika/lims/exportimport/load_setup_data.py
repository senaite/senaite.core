from DateTime import DateTime
from Persistence import PersistentMapping
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import PMF
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import sortable_title
from cStringIO import StringIO
from openpyxl.reader.excel import load_workbook
from os.path import join
from pkg_resources import resource_listdir, resource_filename, ResourceManager
from zipfile import ZipFile, ZIP_DEFLATED
from zope.app.component.hooks import getSite
import Globals
import json
import re
import tempfile
import transaction
import zope

class LoadSetupData(BrowserView):
    template = ViewPageTemplateFile("import.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

        self.portal_catalog = getToolByName(self.context, 'portal_catalog')
        self.bc = bsc = getToolByName(self.context, 'bika_catalog')
        self.bsc = bsc = getToolByName(self.context, 'bika_setup_catalog')
        self.reference_catalog = getToolByName(self.context, REFERENCE_CATALOG)
        self.portal_registration = getToolByName(self.context, 'portal_registration')
        self.portal_groups = getToolByName(self.context, 'portal_groups')
        self.portal_membership = getToolByName(self.context, 'portal_membership')
        self.plone_utils = getToolByName(self.context, 'plone_utils')
        self.uc = getToolByName(context, 'uid_catalog')
        self.bac = getToolByName(context, 'bika_analysis_catalog')
        self.bsc = getToolByName(context, 'bika_setup_catalog')
        self.wf = getToolByName(context, 'portal_workflow')

        # dependencies to resolve
        self.deferred = []

        self.request.set('disable_border', 1)

    def set_wf_history(self, obj, hist):
        old_history = eval(hist)
        for wf_id,wfh in old_history.items():
            if obj.portal_type == "AnalysisRequest" and wf_id == "bika_analysis_workflow":
                wf_id = "bika_ar_workflow"
            if wf_id == 'bika_standardsample_workflow':
                wf_id = 'bika_referencesample_workflow'
            if wf_id == 'bika_standardanalysis_workflow':
                wf_id = 'bika_referenceanalysis_workflow'
            for state in wfh:
                if state == wfh[-1]:
                    set_permissions=False
                else:
                    set_permissions=True
                changeWorkflowState(obj, wf_id, state['review_state'],
                                    set_permissions=set_permissions,
                                    portal_workflow=self.wf, **state)

    def solve_deferred(self):
        # walk through self.deferred, linking ReferenceFields as we go
        unsolved = []
        for d in self.deferred:
            src_obj = d['src_obj']
            src_field = src_obj.getField(d['src_field'])
            multiValued = src_field.multiValued
            src_mutator = src_field.getMutator(src_obj)
            src_accessor = src_field.getAccessor(src_obj)

            tool = getToolByName(self.context, d['dest_catalog'])
            proxies = tool(d['dest_query'])
            if len(proxies) > 0:
                obj = proxies[0].getObject()
                if multiValued:
                    value = src_accessor()
                    value.append(obj.UID())
                else:
                    value = obj.UID()
                src_mutator(value)
            else:
                unsolved.append(d)
        self.deferred = unsolved
        return len(unsolved)

    def __call__(self):
        form = self.request.form

        portal = getSite()

        wb = None
        if 'existing' in form and form['existing']:
            fn = form['existing']
            self.dataset_name = fn
            filename = resource_filename("bika.lims", "setupdata/%s/%s.xlsx" % (fn, fn))
            wb = load_workbook(filename = filename)
        elif 'file' in form and form['file']:
            tmp = tempfile.mktemp()
            file_content = form['file'].read()
            open(tmp, 'wb').write(file_content)
            wb = load_workbook(filename=tmp)
            self.dataset_name = 'uploaded'

        assert(wb != None)

        sheets = {}
        self.nr_rows = 0
        for sheetname in wb.get_sheet_names():
            if len(sheetname) > 31: print sheetname
            sheets[sheetname] = wb.get_sheet_by_name(sheetname)
            self.nr_rows += sheets[sheetname].get_highest_row()

        self.load_lab_information(sheets['Lab Information'])
        self.load_lab_contacts(sheets['Lab Contacts'])
        self.load_lab_departments(sheets['Lab Departments'])
        self.load_clients(sheets['Clients'])
        self.load_client_contacts(sheets['Client Contacts'])
        self.load_containertypes(sheets["Container Types"])
        self.load_preservations(sheets["Preservations"])
        self.load_containers(sheets["Containers"])
        self.load_instruments(sheets['Instruments'])
        self.load_sample_matrices(sheets['Sample Matrices'])
        self.load_sample_types(sheets['Sample Types'])
        self.load_sample_points(sheets['Sample Points'])
        self.link_samplepoint_sampletype(sheets['Sample Point Sample Types'])
        self.load_analysis_categories(sheets['Analysis Categories'])
        self.load_methods(sheets['Methods'])
        self.load_interim_fields(sheets['Calculation Interim Fields'])
        #self.load_lab_products(sheets['Lab Products'])
        self.load_sampling_deviations(sheets['Sampling Deviations'])
        self.load_reference_manufacturers(sheets['Reference Manufacturers'])

        self.load_calculations(sheets['Calculations'])
        self.load_analysis_services(sheets['Analysis Services'])
        self.service_result_options(sheets['AnalysisService ResultOptions'])
        self.service_uncertainties(sheets['Analysis Service Uncertainties'])

        self.load_analysis_specifications(sheets['Analysis Specifications'])
        self.load_analysis_profile_services(sheets['Analysis Profile Services'])
        self.load_analysis_profiles(sheets['Analysis Profiles'])
        self.load_artemplate_analyses(sheets['AR Template Analyses'])
        self.load_artemplate_partitions(sheets['AR Template Partitions'])
        self.load_artemplates(sheets['AR Templates'])
        self.load_reference_definition_results(sheets['Reference Definition Results'])
        self.load_reference_definitions(sheets['Reference Definitions'])
        self.load_reference_suppliers(sheets['Reference Suppliers'])
        self.load_reference_supplier_contacts(sheets['Reference Supplier Contacts'])

        if 'Worksheet Template Layouts' in sheets:
            self.load_wst_layouts(sheets['Worksheet Template Layouts'])
        if 'Worksheet Template Services' in sheets:
            self.load_wst_services(sheets['Worksheet Template Services'])
        if 'Worksheet Templates' in sheets:
            self.load_worksheet_templates(sheets['Worksheet Templates'])

#        if 'Reference Sample Results' in sheets:
#            self.load_reference_sample_results(sheets['Reference Sample Results'])
#        if 'Reference Samples' in sheets:
#            self.load_reference_samples(sheets['Reference Samples'])
#        if 'Reference Analyses Interims' in sheets:
#            self.load_reference_analyses_interims(sheets['Reference Analyses Interims'])
#        if 'Reference Analyses' in sheets:
#            self.load_reference_analyses(sheets['Reference Analyses'])
#        if 'Samples' in sheets:
#            self.load_samples(sheets['Samples'])
#        if 'AR CCContacts' in sheets:
#            self.load_arccs(sheets['AR CCContacts'])
#        if 'Analysis Requests' in sheets:
#            self.load_ars(sheets['Analysis Requests'])
#        if 'Analyses Interims' in sheets:
#            self.load_analyses_interims(sheets['Analyses Interims'])
#        if 'Analyses' in sheets:
#            self.load_analyses(sheets['Analyses'])
#        if 'Analysis Requests' in sheets:
#            for arid, wfh in self.ar_workflows.items():
#                self.set_wf_history(self.ars[arid], wfh)
#        if 'Worksheets' in sheets:
#            self.load_worksheets(sheets['Worksheets'])
#        if 'Duplicate Analyses Interims' in sheets:
#            self.load_duplicate_interims(sheets['Duplicate Analyses Interims'])
#        if 'Duplicate Analyses' in sheets:
#            self.load_duplicate_analyses(sheets['Duplicate Analyses'])
#        if 'Worksheet Layouts' in sheets:
#            self.load_worksheet_layouts(sheets['Worksheet Layouts'])

        self.load_bika_setup(sheets['Setup'])
        if 'ID Prefixes' in sheets:
            self.load_id_prefixes(sheets['ID Prefixes'])
        if 'Attachment Types' in sheets:
            self.load_attachment_types(sheets['Attachment Types'])

        check = len(self.deferred)
        while len(self.deferred) > 0:
            new = self.solve_deferred()
            logger.info("solved %s of %s deferred references" % (check - new, check))
            if new == check:
                raise Exception("%s unsolved deferred references: %s"%(len(self.deferred), self.deferred))
            check = new

        logger.info("Rebuilding bika_setup_catalog")
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        bsc.clearFindAndRebuild()
        logger.info("Rebuilding bika_catalog")
        bc = getToolByName(self.context, 'bika_catalog')
        bc.clearFindAndRebuild()
        logger.info("Rebuilding bika_analysis_catalog")
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        bac.clearFindAndRebuild()


        message = PMF("Changes saved.")
        self.plone_utils.addPortalMessage(message)
        self.request.RESPONSE.redirect(portal.absolute_url())

    def load_bika_setup(self,sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        values = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            values[row['Field']] = row['Value']

        DSL = {'days': int(values['DefaultSampleLifetime_days']),
               'hours': int(values['DefaultSampleLifetime_hours']),
               'minutes': int(values['DefaultSampleLifetime_minutes']),
               }

        self.context.bika_setup.edit(
            PasswordLifetime = int(values['PasswordLifetime']),
            AutoLogOff = int(values['AutoLogOff']),
            Currency = values['Currency'],
            MemberDiscount = str(float(values['MemberDiscount'])),
            VAT = str(float(values['VAT'])),
            MinimumResults = int(values['MinimumResults']),
            BatchEmail = int(values['BatchEmail']),
##            BatchFax = int(values['BatchFax']),
##            SMSGatewayAddress = values['SMSGatewayAddress'],
            SamplingWorkflowEnabled = values['SamplingWorkflowEnabled'],
            CategoriseAnalysisServices = values['CategoriseAnalysisServices'],
            DryMatterService = self.services.get(values['DryMatterService'], ''),
            ARImportOption = values['ARImportOption'],
            ARAttachmentOption = values['ARAttachmentOption'],
            AnalysisAttachmentOption = values['AnalysisAttachmentOption'],
            DefaultSampleLifetime = DSL,
            AutoPrintLabels = values['AutoPrintLabels'].lower(),
            AutoLabelSize = values['AutoLabelSize'].lower(),
            YearInPrefix = values['YearInPrefix'],
            SampleIDPadding = int(values['SampleIDPadding']),
            ARIDPadding = int(values['ARIDPadding']),
            ExternalIDServer = values['ExternalIDServer'] and True or False,
            IDServerURL = values['IDServerURL'],
        )

    def load_id_prefixes(self,sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        prefixes = self.context.bika_setup.getPrefixes()
        for row in rows[3:]:
            row = dict(zip(fields, row))
            # remove existing prefix from list
            prefixes = [p for p in prefixes
                        if p['portal_type'] != row['portal_type']]
            # add new prefix to list
            prefixes.append({'portal_type': row['portal_type'],
                             'padding': row['padding'],
                             'prefix': row['prefix']})
        self.context.bika_setup.setPrefixes(prefixes)

    def load_containertypes(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_containertypes
        self.containertypes = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('ContainerType', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.containertypes[unicode(row['title'])] = obj


    def load_preservations(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_preservations
        self.preservations = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('Preservation', id = 'tmp')
            obj = folder[_id]
            RP = {'days': int(row['RetentionPeriod_days']),
                  'hours': int(row['RetentionPeriod_hours']),
                  'minutes': int(row['RetentionPeriod_minutes']),
                  }

            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     RetentionPeriod = RP
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.preservations[unicode(row['title'])] = obj


    def load_containers(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_containers
        self.containers = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('Container', id = 'tmp')
            obj = folder[_id]
            P = row['Preservation_title']
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Capacity = unicode(row['Capacity']),
                     PrePreserved = row['PrePreserved'] and row['PrePreserved'] or False)
            if row['ContainerType_title']:
                obj.setContainerType(self.containertypes[row['ContainerType_title']])
            if P:
                obj.setPreservation(self.preservations[P])
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.containers[unicode(row['title'])] = obj


    def load_lab_information(self, sheet):
        self.departments = {}
        laboratory = self.context.bika_setup.laboratory
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        values = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            values[row['Field']] = row['Value']

        addresses = {}
        for add_type in ['Physical', 'Postal', 'Billing']:
            addresses[add_type] = {}
            for key in ['Address', 'City', 'State', 'Zip', 'Country']:
                addresses[add_type][key] = values["%s_%s" % (add_type, key)]

        if values['AccreditationBodyLogo']:
            file_title = sortable_title(obj, values['AccreditationBodyLogo'])
            path = resource_filename("bika.lims","setupdata/%s/%s" \
                                     % (self.dataset_name, row['AccreditationBodyLogo']))
            file_data = open(path, "rb").read()
        else:
            file_data = None

        laboratory.edit(
            Name = unicode(values['Name']),
            LabURL = unicode(values['LabURL']),
            Confidence = unicode(values['Confidence']),
            LaboratoryAccredited = values['LaboratoryAccredited'],
            AccreditationBodyLong = unicode(values['AccreditationBodyLong']),
            AccreditationBody = unicode(values['AccreditationBody']),
            AccreditationBodyURL = unicode(values['AccreditationBodyURL']),
            Accreditation = unicode(values['Accreditation']),
            AccreditationReference = unicode(values['AccreditationReference']),
            AccreditationBodyLogo = file_data,
            TaxNumber = unicode(values['TaxNumber']),
            Phone = unicode(values['Phone']),
            Fax = unicode(values['Fax']),
            EmailAddress = unicode(values['EmailAddress']),
            PhysicalAddress = addresses['Physical'],
            PostalAddress = addresses['Postal'],
            BillingAddress = addresses['Billing']
        )

    def load_lab_contacts(self, sheet):
        self.lab_contacts = {}
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_labcontacts
        for row in rows[3:]:
            row = dict(zip(fields, row))

            ## Create LabContact

            if row['Signature']:
                file_title = sortable_title(obj, values['AccreditationBodyLogo'])
                path = resource_filename("bika.lims","setupdata/%s/%s" \
                                         % (self.dataset_name, row['MethodDocument']))
                file_data = open(path, "rb").read()
            else:
                file_data = None

            _id = folder.invokeFactory('LabContact', id='tmp')
            obj = folder[_id]
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            Fullname = unicode(row['Firstname']) + " " + unicode(row['Surname'])
            obj.edit(
                title = Fullname,
                Salutation = unicode(row['Salutation']),
                Firstname = unicode(row['Firstname']),
                Surname = unicode(row['Surname']),
                EmailAddress = unicode(row['EmailAddress']),
                BusinessPhone = unicode(row['BusinessPhone']),
                BusinessFax = unicode(row['BusinessFax']),
                HomePhone = unicode(row['HomePhone']),
                MobilePhone = unicode(row['MobilePhone']),
                JobTitle = unicode(row['JobTitle']),
                Username = unicode(row['Username']),
                Signature = file_data
            )
            self.lab_contacts[Fullname] = obj

            if row['Department_title']:
                self.deferred.append({'src_obj': obj,
                                      'src_field': 'Department',
                                      'dest_catalog': 'bika_setup_catalog',
                                      'dest_query': {'portal_type':'Department',
                                                     'title':row['Department_title']}})

            ## Create Plone user
            if(row['Username']):
                member = self.portal_registration.addMember(
                    unicode(row['Username']),
                    unicode(row['Password']),
                    properties = {
                        'username': unicode(row['Username']),
                        'email': unicode(row['EmailAddress']),
                        'fullname': Fullname}
                    )
                group_ids = [g.strip() for g in unicode(row['Groups']).split(',')]
                role_ids = [r.strip() for r in unicode(row['Roles']).split(',')]
                # Add user to all specified groups
                for group_id in group_ids:
                    group = self.portal_groups.getGroupById(group_id)
                    if group:
                        group.addMember(unicode(row['Username']))
                # Add user to all specified roles
                for role_id in role_ids:
                    member._addRole(role_id)
                # If user is in LabManagers, add Owner local role on clients folder
                if 'LabManager' in group_ids:
                    self.context.clients.manage_setLocalRoles(unicode(row['Username']), ['Owner',] )


    def load_lab_departments(self, sheet):
        self.departments = {}
        lab_contacts = [o.getObject() for o in self.bsc(portal_type="LabContact")]
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_departments
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('Department', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            manager = None
            for contact in lab_contacts:
                if contact.getUsername() == unicode(row['LabContact_Username']):
                    manager = contact
                    break
            if not manager:
                message = "Error: lookup of '%s' in LabContacts/Username failed."%unicode(row['LabContact_Username'])
                self.plone_utils.addPortalMessage(message)
                return self.template()
            obj.setManager(manager.UID())
            self.departments[unicode(row['title'])] = obj
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def load_clients(self, sheet):
        self.clients = {}
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.clients
        for row in rows[3:]:
            row = dict(zip(fields, row))

            addresses = {}
            for add_type in ['Physical', 'Postal', 'Billing']:
                addresses[add_type] = {}
                for key in ['Address', 'City', 'State', 'Zip', 'Country']:
                    addresses[add_type][key] = row["%s_%s" % (add_type, key)]

            _id = folder.invokeFactory('Client', id = 'tmp')
            obj = folder[_id]
            obj.edit(Name = unicode(row['Name']),
                     ClientID = unicode(row['ClientID']),
                     MemberDiscountApplies = row['MemberDiscountApplies'] and True or False,
                     BulkDiscount = row['BulkDiscount'] and True or False,
                     TaxNumber = unicode(row['TaxNumber']),
                     Phone = unicode(row['Phone']),
                     Fax = unicode(row['Fax']),
                     EmailAddress = unicode(row['EmailAddress']),
                     PhysicalAddress = addresses['Physical'],
                     PostalAddress = addresses['Postal'],
                     BillingAddress = addresses['Billing'],
                     AccountNumber = unicode(row['AccountNumber'])
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.clients[unicode(row['Name'])] = obj

    def load_client_contacts(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.clients
        self.client_contacts = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            client = self.portal_catalog(portal_type = "Client",
                                         Title = unicode(row['Client_title']))
            if len(client) == 0:
                raise IndexError("Client invalid: '%s'" % unicode(row['Client_title']))
            client = client[0].getObject()
            _id = client.invokeFactory('Contact', id = 'tmp')
            contact = client[_id]
            fullname = "%(Firstname)s %(Surname)s" % row
            addresses = {}
            for add_type in ['Physical', 'Postal']:
                addresses[add_type] = {}
                for key in ['Address', 'City', 'State', 'Zip', 'Country']:
                    addresses[add_type][key] = row["%s_%s" % (add_type, key)]
            contact.edit(Salutation = unicode(row['Salutation']),
                         Firstname = unicode(row['Firstname']),
                         Surname = unicode(row['Surname']),
                         Username = unicode(row['Username']),
                         JobTitle = unicode(row['JobTitle']),
                         Department = unicode(row['Department']),
                         BusinessPhone = unicode(row['BusinessPhone']),
                         BusinessFax = unicode(row['BusinessFax']),
                         HomePhone = unicode(row['HomePhone']),
                         MobilePhone = unicode(row['MobilePhone']),
                         EmailAddress = unicode(row['EmailAddress']),
                         PublicationPreference = unicode(row['PublicationPreference']).split(","),
                         AttachmentsPermitted = row['AttachmentsPermitted'] and True or False,
                         PhysicalAddress = addresses['Physical'],
                         PostalAddress = addresses['Postal'],
            )

            contact.unmarkCreationFlag()
            renameAfterCreation(contact)
            self.client_contacts[fullname] = contact

            # CC Contacts
            if row['CCContacts']:
                for _fullname in row['CCContacts'].split(","):
                    self.deferred.append({'src_obj': contact,
                                          'src_field': 'CCContact',
                                          'dest_catalog': 'portal_catalog',
                                          'dest_query': {'portal_type':'Contact',
                                                         'getFullname':_fullname}})

            ## Create Plone user
            if(row['Username']):
                member = self.portal_registration.addMember(
                    unicode(row['Username']),
                    unicode(row['Password']),
                    properties = {
                        'username': unicode(row['Username']),
                        'email': unicode(row['EmailAddress']),
                        'fullname': fullname}
                    )
                contact.aq_parent.manage_setLocalRoles(unicode(row['Username']), ['Owner',] )
                # add user to Clients group
                group = self.portal_groups.getGroupById('Clients')
                group.addMember(row['Username'])


    def load_instruments(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_instruments
        self.instruments = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('Instrument', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Type = unicode(row['Type']),
                     Brand = unicode(row['Brand']),
                     Model = unicode(row['Model']),
                     SerialNo = unicode(row['SerialNo']),
                     CalibrationCertificate = unicode(row['CalibrationCertificate']),
                     CalibrationExpiryDate = unicode(row['CalibrationExpiryDate']),
                     DataInterface = row['DataInterface'])
            self.instruments[unicode(row['title'])] = obj
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


    def load_sample_points(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        setup_folder = self.context.bika_setup.bika_samplepoints
        self.samplepoints = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if 'Client_title' in fields and row['Client_title']:
                client_title = unicode(row['Client_title'])
                client = self.portal_catalog(portal_type = "Client",
                                             Title = client_title)
                if len(client) == 0:
                    raise IndexError("Sample Point %s: Client invalid: '%s'" %\
                                     (row['title'], client_title))
                folder = client[0].getObject()
            else:
                folder = setup_folder

            if row['Latitude']: logger.log("Ignored SamplePoint Latitude", 'error')
            if row['Longitude']: logger.log("Ignored SamplePoint Longitude", 'error')

            _id = folder.invokeFactory('SamplePoint', id = 'tmp')
            obj = folder[_id]
            self.samplepoints[row['title']] = obj
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Composite = row['description'] and True or False,
                     Elevation = unicode(row['Elevation']),
                     SampleTypes = row['SampleType_title'] and self.sampletypes[row['SampleType_title']] or []
                     )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def load_sample_types(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_sampletypes
        self.sampletypes = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('SampleType', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     RetentionPeriod = {'days':row['RetentionPeriod'],'hours':0,'minutes':0},
                     Hazardoous = row['Hazardous'] and True or False,
                     SampleMatrix = row['SampleMatrix_title'] and self.samplematrices[row['SampleMatrix_title']] or None,
                     Prefix = unicode(row['Prefix']),
                     MinimumVolume = unicode(row['MinimumVolume']),
                     ContainerType = row['ContainerType_title'] and self.containertypes[row['ContainerType_title']] or None
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.sampletypes[row['title']] = obj

    def link_samplepoint_sampletype(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        for row in rows[3:]:
            row = dict(zip(fields, row))

            st = self.sampletypes[row['SampleType_title']]
            sp = self.samplepoints[row['SamplePoint_title']]

            sampletypes = sp.getSampleTypes()
            if st not in sampletypes:
                sampletypes.append(st)
                sp.setSampleTypes(sampletypes)

            samplepoints = st.getSamplePoints()
            if sp not in samplepoints:
                samplepoints.append(sp)
                st.setSamplePoints(samplepoints)

    def load_sampling_deviations(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_samplingdeviations
        self.samplingdeviations = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('SamplingDeviation', id = 'tmp')
            obj = folder[_id]
            self.samplingdeviations[row['title']] = obj.UID()
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def load_sample_matrices(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_samplematrices
        self.samplematrices = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('SampleMatrix', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.samplematrices[row['title']] = obj

    def load_analysis_categories(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_analysiscategories
        self.cats = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('AnalysisCategory', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            if row['Department_title']:
                obj.setDepartment(self.departments[unicode(row['Department_title'])].UID())
            self.cats[unicode(row['title'])] = obj
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def load_methods(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.methods
        self.methods = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('Method', id = 'tmp')
            obj = folder[_id]

            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Instructions = unicode(row['Instructions']))

            if row['MethodDocument']:
                file_title = sortable_title(obj, row['MethodDocument'])
                path = resource_filename("bika.lims",
                                         "setupdata/%s/%s" \
                                         % (self.dataset_name, row['MethodDocument']))
                #file_id = obj.invokeFactory("File", id=row['MethodDocument'])
                #thisfile = obj[file_id]
                file_data = open(path, "rb").read()
                obj.setMethodDocument(file_data)

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.methods[unicode(row['title'])] = obj

    def load_analysis_services(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_analysisservices
        services = []
        self.services = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))

            _id = folder.invokeFactory('AnalysisService', id = 'tmp')
            obj = folder[_id]
            MTA = {'days': int(row['MaxTimeAllowed_days']),
                   'hours': int(row['MaxTimeAllowed_hours']),
                   'minutes': int(row['MaxTimeAllowed_minutes']),
                   }
            obj.edit(
                title = unicode(row['title']),
                description = row['description'] and unicode(row['description']) or '',
                Keyword = unicode(row['Keyword']),
                PointOfCapture = unicode(row['PointOfCapture']),
                Category = self.cats[unicode(row['AnalysisCategory_title'])].UID(),
                Department = self.departments[unicode(row['Department_title'])].UID(),
                ReportDryMatter = row['ReportDryMatter'] and True or False,
                AttachmentOption = row['Attachment'][0].lower(),
                Unit = row['Unit'] and unicode(row['Unit']) or None,
                Precision = unicode(row['Precision']),
                MaxTimeAllowed = MTA,
                Price = "%02f" % float(row['Price']),
                BulkPrice = "%02f" % float(row['BulkPrice']),
                VAT = "%02f" % float(row['VAT']),
                Method = row['Method'] and self.methods[unicode(row['Method'])] or None,
                Instrument = row['Instrument_title'] and self.instruments[row['Instrument_title']] or None,
                Calculation = row['Calculation_title'] and self.calcs[row['Calculation_title']] or None,
                DuplicateVariation = "%02f" % float(row['DuplicateVariation']),
                Accredited = row['Accredited'] and True or False
            )
            service_obj = obj
            self.services[row['title']] = obj
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def service_result_options(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.interim_fields = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            service = self.services[row['Service_title']]
            sro = service.getResultOptions()
            sro.append({'ResultValue':row['ResultValue'],
                        'ResultText':row['ResultText']})
            service.setResultOptions(sro)

    def service_uncertainties(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.interim_fields = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            service = self.services[row['Service_title']]
            sru = service.getUncertainties()
            sru.append({'intercept_min':row['Range Min'],
                        'intercept_max':row['Range Max'],
                        'errorvalue': row['Uncertainty Value']})
            service.setUncertainties(sru)


    def load_interim_fields(self, sheet):
        # Read all InterimFields into self.interim_fields
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.interim_fields = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            calc_title = row['Calculation_title']
            if calc_title not in self.interim_fields.keys():
                self.interim_fields[calc_title] = []
            self.interim_fields[calc_title].append({
                'keyword': unicode(row['keyword']),
                'title': unicode(row['title']),
                'type': 'int',
                'value': unicode(row['value']),
                'unit': unicode(row['unit'] and row['unit'] or '')})

    def load_calculations(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        calcs = []
        self.calcs = {}
        folder = self.context.bika_setup.bika_calculations
        for row in rows[3:]:
            row = dict(zip(fields, row))

            calc_title = unicode(row['title'])
            calc_interims = self.interim_fields.get(calc_title, [])
            formula = unicode(row['Formula'])
            # scan formula for dep services
            keywords = re.compile(r"\[([^\]]+)\]").findall(formula)
            # remove interims from deps
            interim_keys = [k['keyword'] for k in calc_interims]
            dep_keywords = [k for k in keywords if k not in interim_keys]

            _id = folder.invokeFactory('Calculation', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = calc_title,
                     description = unicode(row['description']),
                     InterimFields = calc_interims,
                     Formula = str(row['Formula']))
            for kw in dep_keywords:
                # If the keyword is in calc_interims, no service dependency gets deferred
                self.deferred.append({'src_obj': obj,
                                      'src_field': 'DependentServices',
                                      'dest_catalog': 'bika_setup_catalog',
                                      'dest_query': {'portal_type':'AnalysisService',
                                                     'getKeyword':kw}})
            calc_obj = obj
            self.calcs[row['title']] = obj
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def load_analysis_profile_services(self, sheet):
        # Read the Analysis Profile Services into self.profile_services
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.profile_services = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if row['Profile'] not in self.profile_services.keys():
                self.profile_services[row['Profile']] = []
            self.profile_services[row['Profile']].append(
                self.services[row['Service']])

    def load_analysis_profiles(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_analysisprofiles
        # Read the Analysis Profile Services into a dict
        self.profiles = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('AnalysisProfile', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     ProfileKey = unicode(row['ProfileKey']))
            obj.setService(self.profile_services[row['title']])
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.profiles[unicode(row['title'])] = obj

    def load_artemplate_analyses(self, sheet):
        # Read the AR Template Services into self.artemplate_analyses
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.artemplate_analyses = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if row['ARTemplate'] not in self.artemplate_analyses.keys():
                self.artemplate_analyses[row['ARTemplate']] = []
            self.artemplate_analyses[row['ARTemplate']].append({
                'service_uid': self.services[row['service_uid']].UID(),
                'partition': row['partition']})

    def load_artemplate_partitions(self, sheet):
        # Read the AR Template Partitions into self.artemplate_partitions
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.artemplate_partitions = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if row['ARTemplate'] not in self.artemplate_partitions.keys():
                self.artemplate_partitions[row['ARTemplate']] = []
            self.artemplate_partitions[row['ARTemplate']].append({
                'part_id': row['part_id'],
                'container_uid': row['container']
                and self.containers[row['container']].UID() or [],
                'preservation_uid': row['preservation']
                and self.preservations[row['preservation']].UID() or row['preservation']})

    def load_artemplates(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.artemplates = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
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
                folder = self.clients[client_title]

            if row['SampleType_title']:
                sampletypes = row['SampleType_title']
            else:
                sampletypes = None
            if row['SamplePoint_title']:
                samplepoints = row['SamplePoint_title']
            else:
                samplepoints = None

            _id = folder.invokeFactory('ARTemplate', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Remarks = unicode(row['Remarks']),
                     ReportDryMatter = bool(row['ReportDryMatter']))
            obj.setSampleType(sampletypes)
            obj.setSamplePoint(samplepoints)
            obj.setPartitions(partitions)
            obj.setAnalyses(analyses)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.artemplates[unicode(row['title'])] = obj.UID()

    def load_reference_definition_results(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.ref_def_results = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if row['ReferenceDefinition_title'] \
               not in self.ref_def_results.keys():
                self.ref_def_results[
                    row['ReferenceDefinition_title']] = []
            self.ref_def_results[
                row['ReferenceDefinition_title']].append({
                    'uid': self.services[row['service']].UID(),
                    'result': row['result'],
                    'min': row['min'],
                    'max': row['max']})

    def load_reference_definitions(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        self.definitions = {}
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_referencedefinitions
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('ReferenceDefinition', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Blank = row['Blank'] and True or False,
                     ReferenceResults = self.ref_def_results.get(row['title'], []),
                     Hazardous = row['Hazardous'] and True or False)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.definitions[unicode(row['title'])] = obj.UID()

    def load_analysis_specifications(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        # First we sort the specs by client/sampletype
        #  { Client: { SampleType: { service, min, max, error }... }... }
        all_specs = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            client_title = row['Client_title'] or 'lab'
            sampletype_title = row['SampleType_title']
            if client_title not in all_specs:
                all_specs[client_title] = {}
            if sampletype_title not in all_specs[client_title]:
                all_specs[client_title][sampletype_title] = []
            all_specs[client_title][sampletype_title].append({
                'keyword': str(self.services[row['service']].getKeyword()),
                'min': str(row['min']),
                'max': str(row['max']),
                'error': str(row['error'])})
        for client, client_specs in all_specs.items():
            if client == 'lab':
                folder = self.context.bika_setup.bika_analysisspecs
            else:
                folder = self.clients[client]
            for sampletype_title, resultsrange in client_specs.items():
                sampletype = self.sampletypes[sampletype_title]
                _id = folder.invokeFactory('AnalysisSpec', id = 'tmp')
                obj = folder[_id]
                obj.edit(
                         title = sampletype.Title(),
                         ResultsRange = resultsrange)
                obj.setSampleType(sampletype.UID())
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)

    def load_reference_manufacturers(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_referencemanufacturers
        self.ref_manufacturers = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('ReferenceManufacturer', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            obj.unmarkCreationFlag()
            self.ref_manufacturers[row['title']] = obj.UID()
            renameAfterCreation(obj)

    def load_reference_suppliers(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_referencesuppliers
        self.ref_suppliers = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('ReferenceSupplier', id = 'tmp')
            obj = folder[_id]
            obj.edit(AccountNumber = unicode(row['AccountNumber']),
                     Name = unicode(row['Name']),
                     EmailAddress = unicode(row['EmailAddress']),
                     Phone = unicode(row['Phone']),
                     Fax = unicode(row['Fax']))
            obj.unmarkCreationFlag()
            self.ref_suppliers[obj.Title()] = obj
            renameAfterCreation(obj)

    def load_reference_supplier_contacts(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if not row['ReferenceSupplier_Name']:
                continue
            folder = self.bsc(portal_type="ReferenceSupplier",
                              Title = row['ReferenceSupplier_Name'])[0].getObject()
            _id = folder.invokeFactory('SupplierContact', id = 'tmp')
            obj = folder[_id]
            obj.edit(
                Firstname = unicode(row['Firstname']),
                Surname = unicode(row['Surname']),
                EmailAddress = unicode(row['EmailAddress']))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

            if 'Username' in row:
##               'Password' in row:
##                self.context.REQUEST.set('username', unicode(row['Username']))
##                self.context.REQUEST.set('password', unicode(row['Password']))
##                self.context.REQUEST.set('email', unicode(row['EmailAddress']))
##                pr = getToolByName(self.context, 'portal_registration')
##                pr.addMember(unicode(row['Username']),
##                             unicode(row['Password']),
##                             properties = {
##                                 'username': unicode(row['Username']),
##                                 'email': unicode(row['EmailAddress']),
##                                 'fullname': " ".join((row['Firstname'],
##                                                       row['Surname']))})
                obj.setUsername(unicode(row['Username']))

    def load_reference_sample_results(self, sheet):
        # Read the Ref Sample Results into self.refsample_results
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.refsample_results = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            refsample_id = row['ReferenceSample_id']
            if not self.refsample_results.has_key(refsample_id):
                self.refsample_results[refsample_id] = []
            self.refsample_results[refsample_id].append({
                'uid': self.services[row['service']].UID(),
                'result': row['result'],
                'min': row['min'],
                'max': row['max']})

    def load_reference_samples(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.ref_samples = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            supplier = self.ref_suppliers[row['ReferenceSupplier_title']]
            supplier.invokeFactory('ReferenceSample', id = row['id'])
            obj = supplier[row['id']]
            ref_def = row['ReferenceDefinition_title']
            ref_def = ref_def and self.definitions[ref_def] or ''
            ref_man = row['ReferenceManufacturer_title']
            ref_man = ref_man and self.ref_manufacturers[ref_man] or ''
            obj.edit(title = unicode(row['id']),
                     description = unicode(row['description']),
                     Blank = row['Blank'],
                     Hazardous = row['Hazardous'],
                     ReferenceResults = self.refsample_results[row['id']],
                     CatalogueNumber = row['CatalogueNumber'],
                     LotNumber = row['LotNumber'],
                     Remarks = row['Remarks'],
                     ExpiryDate = row['ExpiryDate'],
                     DateSampled = row['DateSampled'],
                     DateReceived = row['DateReceived'],
                     DateOpened = row['DateOpened'],
                     DateExpired = row['DateExpired'],
                     DateDisposed = row['DateDisposed']
                     )
            obj.setReferenceDefinition(ref_def)
            obj.setReferenceManufacturer(ref_man)
            obj.setCreators(row['creator'])
            obj.setCreationDate(row['created'])
            self.set_wf_history(obj, row['workflow_history'])
            self.ref_samples[row['id']] = obj
            obj.unmarkCreationFlag()

    def load_reference_analyses_interims(self, sheet):
        # Read the Ref Analyses interims self.refinterim_results
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.refinterim_results = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            refanalysis_id = row['ReferenceAnalysis_id']
            if not self.refanalysis_results.has_key(refanalysis_id):
                self.refanalysis_results[refanalysis_id] = []
            self.refanalysis_results[refanalysis_id].append({
                'keyword': row['keyword'],
                'title': row['title'],
                'value': row['value']})

    def load_reference_analyses(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        for row in rows[3:]:
            row = dict(zip(fields, row))
            service = self.services[row['AnalysisService_title']]
            # Analyses are keyed/named by service keyword
            sample = self.ref_samples[row['ReferenceSample_id']]
            sample.invokeFactory('ReferenceAnalysis', id = row['id'])
            obj = sample[row['id']]
            obj.edit(title = unicode(row['id']),
                     ReferenceType = row['ReferenceType'],
                     Result = row['Result'],
                     ResultDM = row['ResultDM'],
                     Analyst = row['Analyst'],
                     Instrument = row['Instrument'],
                     Retested = row['Retested']
                     )
            obj.setService(service)
            obj.setCreators(row['creator'])
            obj.setCreationDate(row['created'])
            self.set_wf_history(obj, row['workflow_history'])
            obj.unmarkCreationFlag()

    def load_attachment_types(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_attachmenttypes
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('AttachmentType', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def load_lab_products(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_labproducts
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('LabProduct', id = 'tmp')
            obj = folder[_id]

            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Volume = unicode(row['Volume']),
                     Unit = unicode(row['Unit'] and row['Unit'] or ''),
                     Price = "%02f" % float(row['Price']))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def load_wst_layouts(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.wst_layouts = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if row['WorksheetTemplate_title'] \
               not in self.wst_layouts.keys():
                self.wst_layouts[
                    row['WorksheetTemplate_title']] = []
            self.wst_layouts[
                row['WorksheetTemplate_title']].append({
                    'pos': row['pos'],
                    'type': unicode(row['type']),
                    'blank_ref': unicode(row['blank_ref']),
                    'control_ref': unicode(row['control_ref']),
                    'dup': row['dup']})

    def load_wst_services(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.wst_services = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if row['WorksheetTemplate_title'] \
               not in self.wst_services.keys():
                self.wst_services[
                    row['WorksheetTemplate_title']] = []
            self.wst_services[
                row['WorksheetTemplate_title']].append(
                    self.services[row['service']].UID())

    def load_worksheet_templates(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_worksheettemplates
        self.wstemplates = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.invokeFactory('WorksheetTemplate', id = 'tmp')
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Layout = self.wst_layouts[row['title']])
            obj.setService(self.wst_services[row['title']])
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            self.wstemplates[row['title']] = obj.UID()

    def load_partition_setup(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        folder = self.context.bika_setup.bika_analysisservices
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if not row['Analysis Service']: continue
            service = self.services[row['Analysis Service']]
            sampletype = self.sampletypes[row['Sample Type']]
            ps = service.getPartitionSetup()
            containers = []
            if row['Container']:
                for c in row['Container'].split(","):
                    c = c.strip()
                    containers.append(self.containers[c].UID())
            preservations = []
            if row['Preservation']:
                for p in row['Preservation'].split(","):
                    p = p.strip()
                    preservations.append(self.preservations[p].UID())
            ps.append({'sampletype': sampletype.UID(),
                       'container':containers,
                       'preservation':preservations,
                       'separate':row['Separate']})
            service.setPartitionSetup(ps)

    def load_samples(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.samples = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            folder = self.clients[row['Client_Name']]
            _id = folder.invokeFactory('Sample', id = row['id'])
            obj = folder[_id]
            self.samples[row['id']] = obj.UID()
            obj.setSampleID(row['id'])
            obj.setClientSampleID(row['ClientSampleID'])
            obj.setSamplingWorkflowEnabled(False)
            obj.setDateSampled(row['DateSampled'])
            obj.setSampler(row['Sampler'])
            obj.setSamplingDate(row['SamplingDate'])
            obj.setDateReceived(row['DateReceived'])
            obj.setRemarks(row['Remarks'])
            obj.setComposite(row['Composite'])
            obj.setDateExpired(row['DateExpired'])
            obj.setDateDisposed(row['DateDisposed'])
            obj.setAdHoc(row['AdHoc'])
            obj.setSampleType(row['SampleType_title'])
            obj.setSamplePoint(row['SamplePoint_title'])
            if row['SamplingDeviation_title']:
                obj.setSamplingDeviation(self.samplingdeviations[row['SamplingDeviation_title']])
            obj.setCreators(row['creator'])
            obj.setCreationDate(row['created'])
            self.set_wf_history(obj, row['workflow_history'])
            review_state = self.wf.getInfoFor(obj, 'review_state')
            obj.unmarkCreationFlag()
            # Create a single partition...
            _id = obj.invokeFactory('SamplePartition', 'part-1')
            part = obj[_id]
            part.setContainer(self.containers['None Specified'])
            part.unmarkCreationFlag()
            changeWorkflowState(part, 'bika_sample_workflow', review_state)
            part.reindexObject()

    def load_arccs(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.arccs = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if row['AnalysisRequest_id'] \
               not in self.arccs.keys():
                self.arccs[row['AnalysisRequest_id']] = []
            self.arccs[row['AnalysisRequest_id']].append(row['Contact_Fullname'])

    def load_ars(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.ars = {}
        # We apply the workflows -after- we add the analyses
        self.ar_workflows = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            folder = self.clients[row['Client_title']]
            _id = folder.invokeFactory('AnalysisRequest', id = row['id'])
            obj = folder[_id]
            self.ars[row['id']] = obj
            obj.edit(
                RequestID = row['id'],
                CCEmails = row['CCEmails'],
                ClientOrderNumber = row['ClientOrderNumber'],
                #Invoice
                InvoiceExclude = row['InvoiceExclude'],
                ReportDryMatter = row['ReportDryMatter'],
                DateReceived = row['DateReceived'],
                DatePublished = row['DatePublished'],
                Remarks = row['Remarks']
            )
            if row['Profile_title']:
                obj.setProfile(self.profiles[row['Profile_title']])
            if row['Template_title']:
                obj.setTemplate(self.artemplates[row['Template_title']])
            obj.setContact(self.client_contacts[row['Contact_Fullname']])
            obj.setSample(self.samples[row['Sample_id']])
            if self.arccs.get(row['id']):
                cc_contacts = [self.client_contacts[cc]
                               for cc in self.arccs.get(row['id'])]
                obj.setCCContact(cc_contacts)
            obj.setCreators(row['creator'])
            obj.setCreationDate(row['created'])
            self.ar_workflows[row['id']] = row['workflow_history']
            obj.unmarkCreationFlag()

    def load_analyses_interims(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.interim_results = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            analysis_id = row['Analysis_id']
            if not self.interim_results.has_key(analysis_id):
                self.interim_results[analysis_id] = []
            self.interim_results[analysis_id].append({
                'keyword': row['keyword'],
                'title': row['title'],
                'value': row['value']})

    def load_analyses(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        for row in rows[3:]:
            row = dict(zip(fields, row))
            service = self.services[row['Service_title']]
            # analyses are keyed/named by keyword
            keyword = service.getKeyword()
            ar = self.ars[row['AnalysisRequest_id']]
            ar.invokeFactory('Analysis', id = keyword)
            obj = ar[keyword]
            obj.edit(
                # Calculation = self.calculations # COU has none set
                # Attachment # COU has none
                Result = row['Result'],
                ResultCaptureDate = '', # COU has none.
                ResultDM = '', # COU has none.
                Retested = row['Retested'],
                MaxTimeAllowed = eval(row['MaxTimeAllowed']),
                DateAnalysisPublished = '', # XXX
                DueDate = row['DueDate'],
                Duration = row['Duration'],
                Earliness = row['Earliness'],
                ReportDryMatter = row['ReportDryMatter'],
                Analyst = row['Analyst'],
                Instrument = row['Instrument'],
                )
            # results are keyed by ID
            if row['id'] in self.interim_results.keys():
                InterimFields = self.interim_results[row['id']],
            part = obj.aq_parent.getSample().objectValues('SamplePartition')[0].UID()
            obj.setSamplePartition(part)
            obj.setService(service.UID())
            obj.setCreators(row['creator'])
            obj.setCreationDate(row['created'])
            self.set_wf_history(obj, row['workflow_history'])
            analyses = ar.objectValues('Analyses')
            analyses = list(analyses)
            analyses.append(obj)
            ar.setAnalyses(analyses)
            obj.unmarkCreationFlag()

    def load_worksheet_layouts(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.ws_layouts = {}
        self.ws_analyses = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if row['Worksheet_id'] not in self.ws_layouts.keys():
                self.ws_layouts[row['Worksheet_id']] = []
                self.ws_analyses[row['Worksheet_id']] = []

            container = self.bc(id=row['container'])[0].getObject()
            container_uid = container.UID()
            try:
                analysis = container[row['analysis']]
            except:
                print "Can not find analysis %s in container %s: SKIP" % (row['analysis'], row['container'])
                continue
            analysis_uid = analysis.UID()

            self.ws_analyses[row['Worksheet_id']].append(analysis_uid)
            self.ws_layouts[row['Worksheet_id']].append({
                'position': row['position'],
                'type': unicode(row['type']),
                'container_uid': container_uid,
                'analysis_uid': analysis_uid,
            })

        for ws_id, wsl in self.ws_layouts.items():
            ws_uid = self.worksheets[row['Worksheet_id']]
            ws = self.uc(UID=ws_uid)[0].getObject()
            ws.setLayout(wsl)
            wsa = self.ws_analyses[ws_id]
            ws.setAnalyses(wsa)

    def load_worksheets(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.worksheets = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            folder = self.context.worksheets
            folder.invokeFactory('Worksheet', id = row['id'])
            obj = folder[row['id']]
            analyses = []
            obj.edit(
                Remarks = row['Remarks'],
                Analyst = row['Analyst']
            )
            if row['WorksheetTemplate_title']:
                obj.setWorksheetTemplate(self.wstemplates[row['WorksheetTemplate_title']])
            obj.setCreators(row['creator'])
            obj.setCreationDate(row['created'])
            self.set_wf_history(obj, row['workflow_history'])
            self.worksheets[row['id']] = obj.UID()
            obj.unmarkCreationFlag()

    def load_duplicate_interims(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        self.d_interim_results = {}
        for row in rows[3:]:
            row = dict(zip(fields, row))
            analysis_id = row['DuplicateAnalysis_id']
            if not self.d_interim_results.has_key(analysis_id):
                self.d_interim_results[analysis_id] = []
            self.d_interim_results[analysis_id].append({
                'keyword': row['keyword'],
                'title': row['title'],
                'value': row['value']})

    def load_duplicate_analyses(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[0]
        for row in rows[3:]:
            row = dict(zip(fields, row))
            ws = self.uc(UID=self.worksheets[row['Worksheet_id']])[0].getObject()
            ws.invokeFactory('DuplicateAnalysis', id = row['id'])
            obj = ws[row['id']]
            obj.edit(
                InterimFields = self.d_interim_results.get(row['id'], []),
                Result = row['Result'],
                ResultDM = '', # XXX
                Retested = row['Retested'],
                Analyst = '', # XXX
                Instrument = '', # XXX
            )
            obj.setCreators(row['creator'])
            obj.setCreationDate(row['created'])
            self.set_wf_history(obj, row['workflow_history'])
            obj.unmarkCreationFlag()


