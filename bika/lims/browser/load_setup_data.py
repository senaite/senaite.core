from App.Common import package_home
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import logger, bikaMessageFactory as _
from cStringIO import StringIO
from openpyxl.reader.excel import load_workbook
from os.path import join
from zipfile import ZipFile, ZIP_DEFLATED
import Globals
import tempfile
import transaction
from xml.etree.ElementTree import XML

class LoadSetupData(BrowserView):
    template = ViewPageTemplateFile("templates/load_setup_data.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.title = _("Load Setup Data")
        self.description = _("Please.")
        # dependencies to resolve
        self.deferred = []

    def __call__(self):
        form = self.request.form

        self.portal_catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_registration = getToolByName(self.context, 'portal_registration')
        self.portal_groups = getToolByName(self.context, 'portal_groups')
        self.portal_membership = getToolByName(self.context, 'portal_membership')
        self.translate = getToolByName(self.context, 'translation_service').translate
        self.plone_utils = getToolByName(self.context, 'plone_utils')
        self.plone_utils = getToolByName(self.context, 'plone_utils')

        tmp = tempfile.mktemp(prefix=Globals.INSTANCE_HOME)
        file_content = 'xlsx' in form and form['xlsx'].read()
        if not file_content:
            self.plone_utils.addPortalMessage(_("No file data submitted.  Please submit "
                                                " a valid Open XML Spreadsheet (.xlsx) file."))
            return self.template()

        open(tmp, "wb").write(file_content)
        wb = load_workbook(filename = tmp)

        sheets = {}
        for sheetname in wb.get_sheet_names():
            sheets[sheetname] = wb.get_sheet_by_name(sheetname)
##        self.load_lab_users(sheets['Lab Users'])
        self.load_lab_contacts(sheets['Lab Contacts'])
        self.load_lab_departments(sheets['Lab Departments'])
        self.load_clients(sheets['Clients'])
        self.load_client_contacts(sheets['Client Contacts'])
        self.load_instruments(sheets['Instruments'])
        self.load_sample_points(sheets['Sample Points'])
        self.load_sample_types(sheets['Sample Types'])
        self.load_analysis_categories(sheets['Analysis Categories'])
        self.load_methods(sheets['Methods'])
        self.load_analysis_services(sheets['Analysis Services'])
        self.load_calculations(sheets['Calculations'])

        self.plone_utils.addPortalMessage(_("Success."))
        return self.template()

    def load_images(self, filename):
        #archive = ZipFile(filename, 'r', ZIP_DEFLATED)
        #self.images = {}
        #for zipinfo in archive.filelist:
        #    if zipinfo.filename.lower().endswith('.xml'):
        #        xml = XML(archive.read(zipinfo.filename))
        #for xmlfile in archive/xl/drawings/*.xml:
        #    drawing = xml.etree.ElementTree.XML(xmlfile.read())
        #drawings = xml.etree.ElementTree.XML
        pass

    def load_lab_users(self, sheet):
        portal_registration = getToolByName(self.context, 'portal_registration')
        portal_groups = getToolByName(self.context, 'portal_groups')
        portal_membership = getToolByName(self.context, 'portal_membership')
        translate = getToolByName(self.context, 'translation_service').translate
        plone_utils = getToolByName(self.context, 'plone_utils')

        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Lab Users' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value
                 for col_nr in range(nr_cols)]
                  for row_nr in range(nr_rows)]
        fields = rows[1]
        for row in rows[3:]:
            row = dict(zip(fields, row))
            portal_registration.addMember(
                row['Username'],
                row['Password'],
                properties = {
                    'username': row['Username'],
                    'email': row['EmailAddress'],
                    'fullname': " ".join((row['Firstname'], row['Surname']))})
            group_ids = [g.strip() for g in row['Groups'].split(',')]
            for group_id in group_ids:
                group = portal_groups.getGroupById(group_id)
                if not group:
                    message = translate(
                        "message_invalid_group",
                        "bika",
                        {'group_id': group_id},
                        self.context,
                        default = "Invalid group: '${group_id}'.")
                    plone_utils.addPortalMessage(message)
                    return self.template()
                group.addMember(row['Username'])
            # If user is in LabManagers, add Owner local role on clients folder
            if 'LabManager' in group_ids:
                portal_membership.setLocalRoles(obj = self.context.clients,
                                                member_ids = (row['Username'],),
                                                member_role = 'Owner')

    def load_lab_contacts(self, sheet):
        self.lab_contacts = []
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Lab Contacts' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_labcontacts
        for row in rows[3:]:
            row = dict(zip(fields, row))
            labcontact_id = folder.generateUniqueId('LabContact')
            folder.invokeFactory('LabContact', id = labcontact_id)
            obj = folder[labcontact_id]
            obj.edit(Firstname = row['Firstname'],
                     Surname = row['Surname'],
                     EmailAddress = row['EmailAddress'],
                     BusinessPhone = row['BusinessPhone'],
                     BusinessFax = row['BusinessFax'],
                     MobilePhone = row['MobilePhone'],
                     JobTitle = row['JobTitle'])
                     # Department = row['Department'],
                     # Signature = row['Signature'],
            row['obj'] = obj
            self.lab_contacts.append(row)
            obj.processForm()

    def load_lab_departments(self, sheet):
        lab_contacts = self.portal_catalog(portal_type="LabContact")
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Lab Departments' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_departments
        for row in rows[3:]:
            row = dict(zip(fields, row))
            dep_id = folder.generateUniqueId('Department')
            folder.invokeFactory('Department', id = dep_id)
            obj = folder[dep_id]
            manager = None
            for contact in lab_contacts:
                contact = contact.getObject()
                if contact.getFullname() == row['_LabContact_Fullname']:
                    manager = contact
                    break
            if not manager:
                message = _("Error: '%s' not in Lab Contacts")
                self.plone_utils.addPortalMessage(message)
                raise Exception(message)
            obj.edit(title = row['title'],
                     description = row['description'],
                     Manager = manager.UID())
            obj.processForm()

            # set importedlab contact's department references
            if hasattr(self, 'lab_contacts'):
                for contact in self.lab_contacts:
                    if contact['Department'] == row['title']:
                        contact['obj'].setDepartment(obj.UID())


    def load_clients(self, sheet):
        self.clients = []
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Clients' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.clients
        for row in rows[3:]:
            row = dict(zip(fields, row))
            client_id = folder.generateUniqueId('Client')
            folder.invokeFactory('Client', id = client_id)
            client = folder[client_id]
            client.edit(AccountNumber = row['AccountNumber'],
                        Name = row['Name'],
                        MemberDiscountApplies = row['MemberDiscountApplies'],
                        EmailAddress = row['EmailAddress'],
                        Phone = row['Telephone'],
                        Fax = row['Fax'])
            client.processForm()

    def load_client_contacts(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Client Contacts' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.clients
        for row in rows[3:]:
            row = dict(zip(fields, row))
            client = self.portal_catalog(portal_type = "Client",
                                         Title = row['_Client_Name'])
            if len(client) != 1:
                raise IndexError(_("Client invalid: '%s'" % row['Client']))
            client = client[0].getObject()
            contact_id = client.generateUniqueId('Contact')
            client.invokeFactory('Contact', id = contact_id)
            contact = client[contact_id]
            cc = self.portal_catalog(portal_type="Contact",
                                     getUsername = [c.strip() for c in row['CC'].split(',')])
            contact.edit(Salutation = row['Salutation'],
                         Firstname = row['Firstname'],
                         Surname = row['Surname'],
                         JobTitle = row['JobTitle'],
                         Department = row['Department'],
                         BusinessPhone = row['BusinessPhone'],
                         BusinessFax = row['BusinessFax'],
                         HomePhone = row['HomePhone'],
                         MobilePhone = row['MobilePhone'],
                         EmailAddress = row['EmailAddress'],
                         PublicationPreference = row['PublicationPreference'],
                         CCContact = [c.UID for c in cc],
                         AttachmentsPermitted = row['AttachmentsPermitted'])

            if 'Username' in row and \
               'EmailAddress' in row and \
               'Password' in row:
                self.context.REQUEST.set('username', row['Username'])
                self.context.REQUEST.set('password', row['Password'])
                self.context.REQUEST.set('email', row['EmailAddress'])
                pr = getToolByName(self.context, 'portal_registration')
                pr.addMember(row['Username'],
                             row['Password'],
                             properties = {
                                 'username': row['Username'],
                                 'email': row['EmailAddress'],
                                 'fullname': " ".join((row['Firstname'],
                                                       row['Surname']))})
                contact.setUsername(row['Username'])

                # Give contact's user an Owner local role on their client
                pm = getToolByName(contact, 'portal_membership')
                pm.setLocalRoles(obj = contact.aq_parent,
                                 member_ids = row['Username'],
                                 member_role = 'Owner')

                # add user to Clients group
                group = self.context.portal_groups.getGroupById('Clients')
                group.addMember(row['Username'])

            contact.processForm()

    def load_instruments(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Instruments' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_instruments
        for row in rows[3:]:
            row = dict(zip(fields, row))
            instrument_id = folder.generateUniqueId('Instrument')
            folder.invokeFactory('Instrument', id = instrument_id)
            instrument = folder[instrument_id]
            instrument.edit(title = row['title'],
                            description = row['description'],
                            Type = row['Type'],
                            Brand = row['Brand'],
                            Model = row['Model'],
                            SerialNo = row['SerialNo'],
                            CalibrationCertificate = row['CalibrationCertificate'],
                            CalibrationExpiryDate = row['CalibrationExpiryDate'])
            instrument.processForm()

    def load_sample_points(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Sample Points' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_samplepoints
        for row in rows[3:]:
            row = dict(zip(fields, row))
            sp_id = folder.generateUniqueId('SamplePoint')
            folder.invokeFactory('SamplePoint', id = sp_id)
            sp = folder[sp_id]
            sp.edit(title = row['title'],
                    description = row['description'],
                    SamplingFrequency = {'days':row['Days'], 'hours':row['Hours'], 'minutes':row['Minutes']},
                    Latitude = "%(lat deg)s %(lat min)s %(lat sec)s %(NS)s" % row,
                    Longitude = "%(long deg)s %(long min)s %(long sec)s %(NS)s" % row,
                    Elevation = row['Elevation'])
            sp.processForm()

    def load_sample_types(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Sample Types' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_sampletypes
        for row in rows[3:]:
            row = dict(zip(fields, row))
            st_id = folder.generateUniqueId('SampleType')
            folder.invokeFactory('SampleType', id = st_id)
            st = folder[st_id]
            st.edit(title = row['title'],
                    description = row['description'],
                    RetentionPeriod = row['RetentionPeriod'],
                    Hazardouus = row['Hazardous'])
            st.processForm()

    def load_analysis_categories(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Analysis Categories' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_analysiscategories
        departments = {}
        for dep in self.portal_catalog(portal_type="AnalysisCategory"):
            departments[dep.Title] = dep
        for row in rows[3:]:
            row = dict(zip(fields, row))
            ac_id = folder.generateUniqueId('AnalysisCategory')
            folder.invokeFactory('AnalysisCategory', id = ac_id)
            ac = folder[ac_id]
            ac.edit(title = row['title'],
                    description = row['description'],
                    Department = departments[row['Department']].UID)
            ac.processForm()

    def load_methods(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Methods' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_methods
        for row in rows[3:]:
            row = dict(zip(fields, row))
            m_id = folder.generateUniqueId('Method')
            folder.invokeFactory('Method', id = m_id)
            obj = folder[m_id]
            obj.edit(title = row['title'],
                     description = row['description'],
                     Instructions = row['Instructions'],
                     MethodDocument = row['MethodDocument'])
            obj.processForm()


    def CreateServiceObjects(self, services):
        defered = 0
        if not hasattr(self, 'service_objs'):
            self.service_objs = {}
        if not self.deferred.has_key('Analysis Services'):
            self.deferred['Analysis Services'] = []
        cats = {}
        for cat in self.portal_catalog(portal_type="AnalysisCategory"):
            cats[cat.Title] = cat.UID
        folder = self.context.bika_setup.bika_analysisservices
        for service in services:
            if not deferred and \
               not row['title'] and \
               row['intercept_min'] and \
               row['intercept_max'] and \
               row['errorvalue']:
                u = {'intercept_min': row['intercept_min'],
                     'intercept_max': row['intercept_max'],
                     'errorvalue': row['errorvalue']}
                service_obj.setUncertainties(
                    service_obj.getUncertainties() + [u]
                )
            if row['Calculation'] and not row['Calculation'] in self.calcs:
                self.deferred['Analysis Services'].append(service)
                deferred = 1
                continue
            deferred = 0
            as_id = folder.generateUniqueId('AnalysisService')
            folder.invokeFactory('AnalysisService', id = as_id)
            obj = folder[as_id]
            obj.edit(title = row['title'],
                     description = row['description'],
                     PointOfCapture = row['PointOfCapture'],
                     Unit = row['Unit'],
                     Category = self.cats[row['Category']],
                     Price = row['Price'],
                     CorporatePrice = row['BulkPrice'],
                     VAT = row['VAT'],
                     Precision = row['Precision'],
                     Accredited = Row['Accredited'],
                     Keyword = row['Keyword'],
                     Calculation = self.calcs[row['Calculation']],
                     MaxTimeAllowed = {'days':row['Days'],
                                       'hours':row['Hours'],
                                       'minutes':row['Minutes']},
                     DuplicateVariation = row['DuplicateVariation'],
                     ReportDryMatter = row['ReportDryMatter'])
            service_obj = obj
            obj.processForm()

    def load_analysis_services(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Analysis Categories' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_analysisservices
        services = []
        for row in rows[3:]:
            row = dict(zip(fields, row))
            services.append(row)
        self.CreateServiceObjects(services)

    def CreateCalculationObjects(self, calcs):
        deferred = 0
        if not hasattr(self, 'calcs'):
            self.calcs = {}
        if not self.deferred.has_key('Calculations'):
            self.deferred['Calculations'] = []
        if not deferred and \
           not folder = self.context.bika_setup.bika_calculations
        for calc in calcs:
            c_id = folder.generateUniqueId('Calculation')
            folder.invokeFactory('Calculation', id = c_id)
            obj = folder[c_id]
            obj.edit(title = row['title'],
                      description = row['description'],
                      DependentServices = [self.service_objs[a] for a in DependentServices],
                      InterimFields = InterimFields,
                      Formula = Formula)
            obj.processForm()
            obj.reindexObject()
            self.calculations[title] = obj.UID()

    def load_calculations(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Calculations' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_analysisservices
        calcs = []
        for row in rows[3:]:
            row = dict(zip(fields, row))
            calcs.append(row)
        self.CreateServiceObjects(calcs)
