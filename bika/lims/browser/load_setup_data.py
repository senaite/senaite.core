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
        self.text = _("The values in the imported spreadsheet will evade validation.")
        # dependencies to resolve
        self.deferred = {}

    def __call__(self):
        form = self.request.form

        self.portal_catalog = getToolByName(self.context, 'portal_catalog')
        self.reference_catalog = getToolByName(self.context, 'reference_catalog')
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
        self.load_prefixes(sheets['Prefixes'])
        self.load_lab_users(sheets['Lab Users'])
        self.load_lab_contacts(sheets['Lab Contacts'])
        self.departments = {}
        self.load_lab_departments(sheets['Lab Departments'])
        self.load_clients(sheets['Clients'])
        self.client_contacts = []
        self.load_client_contacts(sheets['Client Contacts'])
        self.fix_client_contact_ccs()
        self.instruments = {}
        self.load_instruments(sheets['Instruments'])
        self.load_sample_points(sheets['Sample Points'])
        self.load_sample_types(sheets['Sample Types'])
        self.cats = {}
        self.load_analysis_categories(sheets['Analysis Categories'])
        self.load_methods(sheets['Methods'])
        self.calcs = {}
        self.services = {}
        self.load_analysis_services(sheets['Analysis Services'])
        self.load_calculations(sheets['Calculations'])

        # process deferred services and calculations which depend on each other
        nr_deferred = 0
        while self.deferred['Analysis Services'] or \
              self.deferred['Calculations']:
            current_deferred = len(self.deferred['Calculations']) + len(self.deferred['Analysis Services'])
            if (self.deferred['Calculations'] or \
                self.deferred['Analysis Services']) and \
               nr_deferred == current_deferred:
                raise Exception("unsolved calc/service references (deferred:%s)"%(self.deferred))
            nr_deferred = current_deferred
            if self.deferred['Analysis Services']:
                defs = self.deferred['Analysis Services']
                self.deferred['Analysis Services'] = []
                self.CreateServiceObjects(defs)
            if self.deferred['Calculations']:
                defs = self.deferred['Calculations']
                self.deferred['Calculations'] = []
                self.CreateCalculationObjects(defs)
            if not self.deferred['Calculations'] and \
               not self.deferred['Analysis Services']:
                break

        self.load_analysis_profiles(sheets['Analysis Profiles'])
        self.load_reference_definitions(sheets['Reference Definitions'])
        self.load_reference_suppliers(sheets['Reference Suppliers'])
        self.load_reference_supplier_contacts(sheets['Reference Supplier Contacts'])
        self.load_attachment_types(sheets['Attachment Types'])
        self.load_lab_products(sheets['Lab Products'])
        self.load_worksheet_templates(sheets['Worksheet Templates'])
        self.load_reference_manufacturers(sheets['Reference Manufacturers'])

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

    def load_prefixes(self, sheet):
        bs = self.context.bika_setup
        prefixes = []
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Prefixes' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        for row in rows[3:]:
            row = dict(zip(fields, row))
            prefixes.append({'portal_type':row['portal_type'],
                             'prefix':row['prefix'],
                             'padding':row['padding']})
        bs.setPrefixes(prefixes)

    def load_reference_manufacturers(self, sheet):
            _id = folder.generateUniqueId('ReferenceManufacturer')
            folder.invokeFactory('ReferenceManufacturer', id = _id)
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            obj.processForm()

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
                unicode(row['Username']),
                unicode(row['Password']),
                properties = {
                    'username': unicode(row['Username']),
                    'email': unicode(row['EmailAddress']),
                    'fullname': " ".join((row['Firstname'], row['Surname']))})
            group_ids = [g.strip() for g in unicode(row['Groups']).split(',')]
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
                group.addMember(unicode(row['Username']))
            # If user is in LabManagers, add Owner local role on clients folder
            if 'LabManager' in group_ids:
                portal_membership.setLocalRoles(obj = self.context.clients,
                                                member_ids = (unicode(row['Username']),),
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
            obj.edit(Firstname = unicode(row['Firstname']),
                     Surname = unicode(row['Surname']),
                     EmailAddress = unicode(row['EmailAddress']),
                     BusinessPhone = unicode(row['BusinessPhone']),
                     BusinessFax = unicode(row['BusinessFax']),
                     MobilePhone = unicode(row['MobilePhone']),
                     JobTitle = unicode(row['JobTitle']))
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
                if contact.getFullname() == unicode(row['_LabContact_Fullname']):
                    manager = contact
                    break
            if not manager:
                message = _("Error: '%s' not in Lab Contacts")
                self.plone_utils.addPortalMessage(message)
                raise Exception(message)
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Manager = manager.UID())
            self.departments[unicode(row['title'])] = obj
            obj.processForm()

            # set importedlab contact's department references
            if hasattr(self, 'lab_contacts'):
                for contact in self.lab_contacts:
                    if contact['Department'] == unicode(row['title']):
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
            obj = folder[client_id]
            obj.edit(AccountNumber = unicode(row['AccountNumber']),
                        Name = unicode(row['Name']),
                        MemberDiscountApplies = row['MemberDiscountApplies'] and True or False,
                        EmailAddress = unicode(row['EmailAddress']),
                        Phone = unicode(row['Telephone']),
                        Fax = unicode(row['Fax']))
            obj.processForm()

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
                                         Title = unicode(row['_Client_Name']))
            if len(client) == 0:
                raise IndexError(_("Client invalid: '%s'" % unicode(row['_Client_Name'])))
            client = client[0].getObject()
            contact_id = client.generateUniqueId('Contact')
            client.invokeFactory('Contact', id = contact_id)
            contact = client[contact_id]
            cc = self.portal_catalog(portal_type="Contact",
                                     getUsername = [c.strip() for c in unicode(row['CC']).split(',')])
            if row['CC'] and not cc:
                row['uid'] = contact.UID()
                self.client_contacts.append(row)
            contact.edit(Salutation = unicode(row['Salutation']),
                         Firstname = unicode(row['Firstname']),
                         Surname = unicode(row['Surname']),
                         JobTitle = unicode(row['JobTitle']),
                         Department = unicode(row['Department']),
                         BusinessPhone = unicode(row['BusinessPhone']),
                         BusinessFax = unicode(row['BusinessFax']),
                         HomePhone = unicode(row['HomePhone']),
                         MobilePhone = unicode(row['MobilePhone']),
                         EmailAddress = unicode(row['EmailAddress']),
                         PublicationPreference = unicode(row['PublicationPreference']),
                         CCContact = [c.UID for c in cc],
                         AttachmentsPermitted = row['AttachmentsPermitted'] and True or False)
            if 'Username' in row and \
               'EmailAddress' in row and \
               'Password' in row:
                self.context.REQUEST.set('username', unicode(row['Username']))
                self.context.REQUEST.set('password', unicode(row['Password']))
                self.context.REQUEST.set('email', unicode(row['EmailAddress']))
                pr = getToolByName(self.context, 'portal_registration')
                try:
                    pr.addMember(unicode(row['Username']),
                                 unicode(row['Password']),
                                 properties = {
                                     'username': unicode(row['Username']),
                                     'email': unicode(row['EmailAddress']),
                                     'fullname': " ".join((unicode(row['Firstname']),
                                                           unicode(row['Surname'])))})
                    contact.setUsername(unicode(row['Username']))
                except ValueError:
                    logger.info("username %s is already in use" % unicode(row['Username']))
                    raise
                # Give contact's user an Owner local role on their client
                pm = getToolByName(contact, 'portal_membership')
                pm.setLocalRoles(obj = contact.aq_parent,
                                 member_ids = unicode(row['Username']),
                                 member_role = 'Owner')

                # add user to Clients group
                group = self.context.portal_groups.getGroupById('Clients')
                group.addMember(row['Username'])

            contact.processForm()

    def fix_client_contact_ccs(self):
        for row in self.client_contacts:
            client = self.portal_catalog(portal_type = "Client",
                                         Title = unicode(row['_Client_Name']))
            contact = self.reference_catalog.lookupObject(row['uid'])
            cc = self.portal_catalog(portal_type="Contact",
                                     getUsername = [c.strip() for c in \
                                                    unicode(row['CC']).split(',')])
            if cc:
                contact.setCCContact([c.UID for c in cc])

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
            obj = folder[instrument_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Type = unicode(row['Type']),
                     Brand = unicode(row['Brand']),
                     Model = unicode(row['Model']),
                     SerialNo = unicode(row['SerialNo']),
                     CalibrationCertificate = unicode(row['CalibrationCertificate']),
                     CalibrationExpiryDate = unicode(row['CalibrationExpiryDate']))
            self.instruments[unicode(row['title'])] = obj
            obj.processForm()

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
            obj = folder[sp_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     SamplingFrequency = {'days':unicode(row['Days']), 'hours':unicode(row['Hours']), 'minutes':unicode(row['Minutes'])},
                     Latitude = "%(lat deg)s %(lat min)s %(lat sec)s %(NS)s" % row,
                     Longitude = "%(long deg)s %(long min)s %(long sec)s %(NS)s" % row,
                     Elevation = unicode(row['Elevation']))
            obj.processForm()

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
            obj = folder[st_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     RetentionPeriod = int(row['RetentionPeriod']),
                     Hazardouus = row['Hazardous'] and True or False)
            obj.processForm()

    def load_analysis_categories(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Analysis Categories' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_analysiscategories
        for row in rows[3:]:
            row = dict(zip(fields, row))
            ac_id = folder.generateUniqueId('AnalysisCategory')
            folder.invokeFactory('AnalysisCategory', id = ac_id)
            obj = folder[ac_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Department = self.departments[unicode(row['Department'])].UID())
            self.cats[unicode(row['title'])] = obj
            obj.processForm()

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
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Instructions = unicode(row['Instructions']))
#                     MethodDocument = row['MethodDocument'])
            obj.processForm()

    def CreateServiceObjects(self, services):
        deferred = 0
        if not hasattr(self, 'service_objs'):
            self.service_objs = {}
        if not self.deferred.has_key('Analysis Services'):
            self.deferred['Analysis Services'] = []
        folder = self.context.bika_setup.bika_analysisservices
        for row in services:
            if not row['title']:
                if deferred:
                    u = {'intercept_min': unicode(row['intercept_min']),
                         'intercept_max': unicode(row['intercept_max']),
                         'errorvalue': unicode(row['errorvalue'])}
                    self.deferred['Analysis Services'][-1]['_uncert'].append(u)
                    continue
                if row['intercept_min'] and \
                   row['intercept_max'] and \
                   row['errorvalue']:
                    u = [{'intercept_min': unicode(row['intercept_min']),
                          'intercept_max': unicode(row['intercept_max']),
                          'errorvalue': unicode(row['errorvalue'])}]
                    service_obj.setUncertainties(
                        service_obj.getUncertainties() + u
                    )
                continue
            if row['Calculation'] and not row['Calculation'] in \
               [c.Title() for c in self.calcs.values()]:
                # remaining uncertainty values in subsequent rows
                # for deferred services get stored here
                if not '_uncert' in row:
                    row['_uncert'] = []
                self.deferred['Analysis Services'].append(row)
                deferred = 1
                continue
            deferred = 0
            as_id = folder.generateUniqueId('AnalysisService')
            folder.invokeFactory('AnalysisService', id = as_id)
            obj = folder[as_id]
            if row['errorvalue']:
                u = [{'intercept_min': unicode(row['intercept_min']),
                     'intercept_max': unicode(row['intercept_max']),
                     'errorvalue': unicode(row['errorvalue'])}]
            else:
                u = []
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     PointOfCapture = unicode(row['PointOfCapture']),
                     Unit = unicode(row['Unit']),
                     Category = self.cats[unicode(row['Category'])].UID(),
                     Price = "%02f" % float(row['Price']),
                     CorporatePrice = "%02f" % float(row['BulkPrice']),
                     VAT = "%02f" % float(row['VAT']),
                     Precision = unicode(row['Precision']),
                     Accredited = row['Accredited'] and True or False,
                     Keyword = unicode(row['Keyword']),
                     MaxTimeAllowed = {'days':unicode(row['Days']),
                                       'hours':unicode(row['Hours']),
                                       'minutes':unicode(row['Minutes'])},
                     DuplicateVariation = "%02f" % float(row['DuplicateVariation']),
                     Uncertanties = u,
                     ReportDryMatter = row['ReportDryMatter'] and True or False)
            if row['Instrument']:
                obj.setInstrument(self.instruments[row['Instrument']].UID())
            if row['Calculation']:
                obj.setCalculation(self.calcs[row['Calculation']])
            if '_uncert' in row:
                obj.setUncertainties(obj.getUncertainties() + row['_uncert'])
            service_obj = obj
            self.services[row['Keyword']] = obj
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
        if not self.deferred.has_key('Calculations'):
            self.deferred['Calculations'] = []
        folder = self.context.bika_setup.bika_calculations
        for row in calcs:
            if not row['title']:
                if deferred:
                    i = {'keyword': unicode(row['interim_keyword']),
                          'title': unicode(row['interim_title']),
                          'type': unicode(row['interim_type']),
                          'value': unicode(row['interim_value']),
                          'unit': unicode(row['interim_unit'])}
                    self.deferred['Calculations'][-1]['_interim'].append(i)
                    continue
                if row['interim_keyword']:
                    i = [{'keyword': unicode(row['interim_keyword']),
                         'title': unicode(row['interim_title']),
                         'type': unicode(row['interim_type']),
                         'value': unicode(row['interim_value']),
                         'unit': unicode(row['interim_unit'])}]
                    calc_obj.setInterimFields(
                        calc_obj.getInterimFields() + i
                    )
                continue
            deps = row['DependentServices'] and \
                [d.strip() for d in unicode(row['DependentServices']).split(",")] or []
            depservices = []
            try:
                depservices = [self.services[d].UID() for d in deps]
            except KeyError:
                pass
            if len(deps) != len(depservices):
                # remaining interims in subsequent rows for deferred
                # calculations go in row/_interim
                if not '_interim' in row:
                    row['_interim'] = []
                self.deferred['Calculations'].append(row)
                deferred = 1
                continue
            deferred = 0
            c_id = folder.generateUniqueId('Calculation')
            folder.invokeFactory('Calculation', id = c_id)
            obj = folder[c_id]
            if row['interim_keyword']:
                i = [{'keyword': unicode(row['interim_keyword']),
                     'title': unicode(row['interim_title']),
                     'type': unicode(row['interim_type']),
                     'value': unicode(row['interim_value']),
                     'unit': unicode(row['interim_unit'])}]
            else:
                i = []
            obj.edit(title = unicode(row['title']),
                      description = unicode(row['description']),
                      DependentServices = depservices,
                      InterimFields = i,
                      Formula = unicode(row['Formula']))
            if '_interim' in row:
                obj.setInterimFields(obj.getInterimFields() + row['_interim'])
            calc_obj = obj
            self.calcs[row['title']] = obj
            obj.processForm()

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
        self.CreateCalculationObjects(calcs)

    def load_analysis_profiles(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Analysis Profiles' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_arprofiles
        for row in rows[3:]:
            row = dict(zip(fields, row))
            m_id = folder.generateUniqueId('ARProfile')
            folder.invokeFactory('ARProfile', id = m_id)
            obj = folder[m_id]
            services = [d.strip() for d in unicode(row['Service']).split(",")]
            proxies = self.portal_catalog(portal_type="AnalysisService",
                                          getKeyword = services)
            if len(proxies) != len(services):
                raise Exception("Analysis Profile services invalid.  Got %s, found %s" %\
                                (services, [p.getKeyword for p in proxies]))

            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Service = [s.UID for s in proxies],
                     ProfileKey = unicode(row['ProfileKey']))
            obj.processForm()

    def load_reference_definitions(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Reference Definitions' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_referencedefinitions
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if row['title']:
                m_id = folder.generateUniqueId('ReferenceDefinition')
                folder.invokeFactory('ReferenceDefinition', id = m_id)
                obj = folder[m_id]
                obj.edit(title = unicode(row['title']),
                         description = unicode(row['description']),
                         Blank = row['Blank'] and True or False,
                         Hazardous = row['Hazardous'] and True or False)
                obj.processForm()
            service = self.services[row['keyword']]
            try: result = int(row['result'])
            except: result = 0
            try: Min = int(row['min'])
            except: Min = 0
            try: Max = int(row['max'])
            except: Max = 0
            obj.setReferenceResults(
                obj.getReferenceResults() + [{'uid': service.UID(),
                                              'result':unicode(result),
                                              'min':unicode(Min),
                                              'max':unicode(Max)}])

    def load_reference_suppliers(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Reference Suppliers' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.referencesuppliers
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.generateUniqueId('ReferenceSupplier')
            folder.invokeFactory('ReferenceSupplier', id = _id)
            obj = folder[_id]
            obj.edit(AccountNumber = unicode(row['AccountNumber']),
                     Name = unicode(row['Name']),
                     EmailAddress = unicode(row['EmailAddress']),
                     Phone = unicode(row['Phone']),
                     Fax = unicode(row['Fax']))
            obj.processForm()

    def load_reference_supplier_contacts(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Reference Supplier Contacts' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        for row in rows[3:]:
            row = dict(zip(fields, row))
            rs = self.portal_catalog(portal_type="ReferenceSupplier",
                                    Title = row['_ReferenceSupplier_Name'])[0].getObject()
            _id = rs.generateUniqueId('ReferenceSupplier')
            rs.invokeFactory('SupplierContact', id = _id)
            obj = rs[_id]
            obj.edit(Firstname = unicode(row['Firstname']),
                     Surname = unicode(row['Surname']),
                     EmailAddress = unicode(row['EmailAddress']))
            obj.processForm()
            if 'Username' in row and \
               'Password' in row:
                self.context.REQUEST.set('username', unicode(row['Username']))
                self.context.REQUEST.set('password', unicode(row['Password']))
                self.context.REQUEST.set('email', unicode(row['EmailAddress']))
                pr = getToolByName(self.context, 'portal_registration')
                pr.addMember(unicode(row['Username']),
                             unicode(row['Password']),
                             properties = {
                                 'username': unicode(row['Username']),
                                 'email': unicode(row['EmailAddress']),
                                 'fullname': " ".join((row['Firstname'],
                                                       row['Surname']))})
                obj.setUsername(unicode(row['Username']))

    def load_attachment_types(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Attachment Types' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_attachmenttypes
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.generateUniqueId('AttachmentType')
            folder.invokeFactory('AttachmentType', id = _id)
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            obj.processForm()

    def load_lab_products(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Lab Products' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_labproducts
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.generateUniqueId('LabProduct')
            folder.invokeFactory('LabProduct', id = _id)
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Volume = unicode(row['Volume']),
                     Unit = unicode(row['Unit']),
                     Price = "%02f" % float(row['Price']))
            obj.processForm()

    def load_worksheet_templates(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Worksheet Templates' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_worksheettemplates
        for row in rows[3:]:
            row = dict(zip(fields, row))
            if not row['title']:
                if row['pos']:
                    l = [{'pos':unicode(row['pos']),
                          'type':unicode(row['type']),
                          'sub':unicode(row['sub']),
                          'dup':unicode(row['dup'])}]
                    wst_obj.setLayout(wst_obj.getLayout() + l)
                continue
            _id = folder.generateUniqueId('WorksheetTemplate')
            folder.invokeFactory('WorksheetTemplate', id = _id)
            obj = folder[_id]
            services = row['Service'] and \
                [d.strip() for d in unicode(row['Service']).split(",")] or \
                []
            proxies = services and self.portal_catalog(portal_type="AnalysisService",
                                                       getKeyword = services) or []
            services = [p.UID for p in proxies]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']),
                     Service = services,
                     Layout = [{'pos':unicode(row['pos']),
                                'type':unicode(row['type']),
                                'sub':unicode(row['sub']),
                                'dup':unicode(row['dup'])}])
            wst_obj = obj
            obj.processForm()

    def load_reference_manufacturers(self, sheet):
        nr_rows = sheet.get_highest_row()
        nr_cols = sheet.get_highest_column()
##        self.request.response.write("<input type='hidden' id='load_section' value='Reference Manufacturers' max='%s'/>"%(nr_rows-3))
##        self.request.response.flush()
        rows = [[sheet.cell(row=row_nr, column=col_nr).value for col_nr in range(nr_cols)] for row_nr in range(nr_rows)]
        fields = rows[1]
        folder = self.context.bika_setup.bika_referencemanufacturers
        for row in rows[3:]:
            row = dict(zip(fields, row))
            _id = folder.generateUniqueId('ReferenceManufacturer')
            folder.invokeFactory('ReferenceManufacturer', id = _id)
            obj = folder[_id]
            obj.edit(title = unicode(row['title']),
                     description = unicode(row['description']))
            obj.processForm()
