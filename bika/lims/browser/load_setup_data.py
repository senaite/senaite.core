from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import logger, bikaMessageFactory as _
from zope.browser.interfaces import IBrowserView
from zope.component import getMultiAdapter
from zope.interface import implements

class LoadSetupData():

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        logger.info("load_setup_data: Laboratory"); self.Laboratory()
        logger.info("load_setup_data: Members and Groups"); self.MembersAndGroups()
        logger.info("load_setup_data: Lab Contacts"); self.LabContacts()
        logger.info("load_setup_data: Prefixes"); self.Prefixes()
        logger.info("load_setup_data: Clients"); self.Clients()
        logger.info("load_setup_data: Departments"); self.Departments()
        logger.info("load_setup_data: Instruments"); self.Instruments()
        logger.info("load_setup_data: Sample Points"); self.SamplePoints()
        logger.info("load_setup_data: Sample Types"); self.SampleTypes()
        logger.info("load_setup_data: Analysis Categories"); self.AnalysisCategories()
        logger.info("load_setup_data: Calculations"); self.Calculations1()
        logger.info("load_setup_data: Analysis Services"); self.AnalysisServices1()
        logger.info("load_setup_data: More Calculations"); self.Calculations2()
        logger.info("load_setup_data: More Analysis Services"); self.AnalysisServices2()
        logger.info("load_setup_data: More Calculations"); self.Calculations3()
        logger.info("load_setup_data: More Analysis Services"); self.AnalysisServices3()
        logger.info("load_setup_data: Methods"); self.Methods()
        logger.info("load_setup_data: Reference Definitions"); self.ReferenceDefinitions()
        logger.info("load_setup_data: Reference Manufacturers"); self.ReferenceManufacturers()
        logger.info("load_setup_data: Reference Suppliers"); self.ReferenceSuppliers()
        logger.info("load_setup_data: Reference Samples"); self.ReferenceSamples()
        logger.info("load_setup_data: Attachment Types"); self.AttachmentTypes()
        logger.info("load_setup_data: Products"); self.Products()
        logger.info("load_setup_data: Worksheet Templates"); self.WorksheetTemplates()

        self.context.plone_utils.addPortalMessage(_(u'Setup data loaded.'), 'info')

        plone = getMultiAdapter((self, self.request), name = "plone_portal_state").portal()
        self.request.response.redirect(plone.absolute_url())

    def Laboratory(self):
        laboratory = self.context.bika_setup.laboratory
        name = 'Bika LIMS'
        name = name.decode('latin-1').encode('utf-8').strip()
        self.context.bika_setup.laboratory.edit(
            Name = name,
            EmailAddress = 'lab@scapp.co.za',
            Confidence = '95',
        )

    def MembersAndGroups(self):
        pr = getToolByName(self.context, 'portal_registration')
        pg = getToolByName(self.context, 'portal_groups')
        pm = getToolByName(self.context, 'portal_membership')
        members = (
            ('Lab Manager', 'labmanager01', 'labmanager01', 'labmanager@scapp.co.za', 'labmanager'),
            ('Lab Clerk', 'labclerk01', 'labclerk01', 'labclerk@scapp.co.za', 'labclerk'),
            ('Lab Techician', 'analyst01', 'analyst01', 'analyst@scapp.co.za', 'analyst'),
            ('Verifier', 'verifier01', 'verifier01', 'verifier@scapp.co.za', 'analyst'),
            ('Publisher', 'publisher01', 'publisher01', 'publisher@scapp.co.za', 'analyst'),
        )
        for fullname, username, password, email, role in members:
            fullname = fullname.decode('latin-1').encode('utf-8').strip()
            try:
                pr.addMember(username,
                             password,
                             properties = {'username': username,
                                           'email': email,
                                           'fullname': fullname}
                             )
                group_id = '%ss' % role
                group = pg.getGroupById(group_id)
                group.addMember(username)
            except:
                pass

            # verifiers and publishers get their normal permissions from a standard lab
            # group. Verifying and publishing permissions are added to this.
            if fullname == 'verifier':
                group = pg.getGroupById('verifiers')
                group.addMember(username)
            if fullname == 'publisher':
                group = pg.getGroupById('publishers')
                group.addMember(username)

        # Give labmanager an Owner local role on clients folder
        clients = self.context.clients
        pm.setLocalRoles(obj = clients,
                         member_ids = [m[1] for m in members if m[-1] == 'labmanager'],
                         member_role = 'Owner')

    def Clients(self):
        folder = self.context.clients
        client_list = (
            ('320', 'Norton Feeds', '1', 'norton@scapp.co.za', '021 5552050', '0215552192', 'Carl', 'Bennett', 'cbennett', 'cbennett@scapp.co.za', 'email'),
            ('330', 'Ostrich Products Inc', '0', 'ostriches@scapp.co.za', '021 5551150', '0215551504', 'Karen', 'Leonard', 'karen', 'karen@scapp.co.za', 'email'),
            ('370', 'Ruff Dog Food', '1', 'ruff@scapp.co.za', '021 5551705', '0215551705', 'Chris', 'Ruffian', 'chris', 'chris@scapp.co.za', 'email'),
            ('470', 'Morton Chickens', '1', 'morton@scapp.co.za', '021 5555264', '0215554557', 'Alfie', 'Faraday', 'alfie', 'faraday@scapp.co.za', 'fax'),
            ('410', 'Sunnyside Egg Farm', '1', 'sunnyside@scapp.co.za', '021 5551663', '0215553295', 'Andre', 'Corbin', 'andre', 'andre@scapp.co.za', 'email'),
            ('420', 'Klaymore Fertilizer', '1', 'klaymore@scapp.co.za', '021 5553026', '0215553157', 'Neil', 'Standard', 'neil', 'neil@scapp.co.za', 'file'),
            ('440', 'Happy Hills Feeds', '1', 'happyhills@scapp.co.za', '021 5554220', '0215554220', 'Rita', 'Mohale', 'rita', 'rita@scapp.co.za', 'fax'),
            ('1624', 'Myrtle Wheat Farm', '0', 'mwf@scapp.co.za', '021 5551901', '0215553417', 'Fred', 'Turner', 'fred', 'turner@scapp.co.za', 'email'),
            ('480', 'Petersville Co-op', '1', 'petersville@scapp.co.za', '021 5551730', '0215551731', 'Gillian', 'Foster', 'gillian', 'gillian@scapp.co.za', 'email'),
        )

        for account_nr, name, member, email, tel, fax, cname, csurname, cusername, cemail, cpubl_pref in client_list:
            name = name.decode('latin-1').encode('utf-8').strip()
            client_id = folder.generateUniqueId('Client')
            folder.invokeFactory(id = client_id, type_name = 'Client')
            client = folder[client_id]
            client.edit(Name = name,
                        AccountNumber = account_nr,
                        MemberDiscountApplies = member,
                        EmailAddress = email,
                        Phone = tel,
                        Fax = fax)
            client.processForm()

            cname = cname.decode('latin-1').encode('utf-8').strip()
            csurname = csurname.decode('latin-1').encode('utf-8').strip()
            contact_id = self.context.generateUniqueId('Contact')
            client.invokeFactory(id = contact_id, type_name = 'Contact')
            contact = client[contact_id]
            contact.edit(Firstname = cname,
                         Surname = csurname,
                         PrimaryEmailAddress = cemail,
                         PublicationPreference = cpubl_pref)

            if cusername and cemail:
                self.context.REQUEST.set('username', cusername)
                self.context.REQUEST.set('password', cusername)
                self.context.REQUEST.set('email', cemail)
                pr = getToolByName(self.context, 'portal_registration')
                pr.addMember(cusername, cusername, properties = self.context.REQUEST)
                contact.setUsername(cusername)

                # Give contact an Owner local role on client
                pm = getToolByName(contact, 'portal_membership')
                pm.setLocalRoles(obj = contact.aq_parent, member_ids = [cusername],
                    member_role = 'Owner')

                # add user to clients group
                group = self.context.portal_groups.getGroupById('clients')
                group.addMember(cusername)
            contact.processForm()
            contact.reindexObject()

    def LabContacts(self):
        contacts = (
            ('John', 'Smith', 'john@scapp.co.za', '021 5551234', '021 5551233', '0825559910'),
            ('Mary', 'Makoeba', 'mary@scapp.co.za', '021 5551236', '021 5551233', '0835558108'),
        )
        folder = self.context.bika_setup.bika_labcontacts
        for firstname, surname, email, tel, fax, mobile in contacts:
            labcontact_id = folder.generateUniqueId('LabContact')
            folder.invokeFactory(id = labcontact_id, type_name = 'LabContact')
            labcontact = folder[labcontact_id]
            labcontact.edit(Firstname = firstname,
                            Surname = surname,
                            EmailAddress = email,
                            BusinessPhone = tel,
                            BusinessFax = fax,
                            MobilePhone = mobile)
            labcontact.processForm()

    def Departments(self):
        # XXX Do Department and LabContact relate?
        # labcontact.department is just a string from Person.
        self.departments = []
        depts = (
            ('Microbiology', 'Microbiology department'),
            ('Chemistry', 'Analytical chemistry department'),
        )
        labcontact = self.context.bika_setup.portal_catalog(portal_type = 'LabContact')[0].getObject()
        folder = self.context.bika_setup.bika_departments
        for title, descr in depts:
            dept_id = folder.generateUniqueId('Department')
            folder.invokeFactory(id = dept_id, type_name = 'Department')
            dept = folder[dept_id]
            dept.edit(title = title,
                      description = descr,
                      Manager = labcontact)
            dept.processForm()
            self.departments.append(dept)

    def Instruments(self):
        folder = self.context.bika_setup.bika_instruments
        instruments = (
            ('Spectrometer', 'Spectrometer', 'Digital', 'Spectronic', '20', '5556545', '', ''),
            ('pH Meter', 'Digital pH meter uses an electrode to measure pH of a solution', 'Digital', 'XBrand', 'Xmodel', '76879878', '', ''),
            ('Vacuum evaporator', 'Buchi type', '', '', '', '', '', ''),
            ('Lypholizer', 'Freeze dryer', 'Mobile', 'NSW', 'NSW-275', '555123', '', ''),
            ('Autoclave', 'Stainless steel autoclave', 'Vertical', 'NSW', 'NSW-227', '555878', '', ''),
        )
        for title, description, type, brand, model, serialno, calibrationcertificate, calibrationexpiry in instruments:
            id = folder.generateUniqueId('Instrument')
            folder.invokeFactory(id = id, type_name = 'Instrument')
            obj = folder[id]
            obj.edit(title = title,
                     description = description,
                     Type = type,
                     Brand = brand,
                     Model = model,
                     SerialNo = serialno,
                     CalibrationCertificate = calibrationcertificate,
                     CalibrationExpiryDate = calibrationexpiry)
            obj.processForm()

    def SamplePoints(self):
        folder = self.context.bika_setup.bika_samplepoints
        samplepoints = (
            ('Plant', 'Production point'),
            ('Bag', 'Retail sample'),
            ('Swab', 'Biomedical sample'),
        )
        for title, description in samplepoints:
            id = folder.generateUniqueId('SamplePoint')
            folder.invokeFactory(id = id, type_name = 'SamplePoint')
            obj = folder[id]
            obj.edit(title = title, description = description)
            obj.processForm()

    def SampleTypes(self):
        folder = self.context.bika_setup.bika_sampletypes
        sampletypes = (
            ('Aartappel/Potato', '', False),
            ('Appelpulp/Apple Pulp', '', False),
            ('Bloedmeel/Blood Meal', '', True),
            ('BR BDR Grower', '', False),
            ('BR BDR Layer Phase 1', '', False),
            ('BR BDR Layer Phase 2', '', False),
            ('BR Grower', '', False),
            ('BR Starter', '', False),
            ('BRD. Layer Phase 2', '', False),
            ('Broodkrummels/Bread Crumbs', '', False),
            ('Brouersgraan/Dist. Grain', '', False),
            ('By-Produk/By-Product', '', True),
            ('Canola', '', False),
            ('Catfish', '', True),
            ('Forelpille/Forel Pellets', '', False),
            ('Fosfaat/Phosfate', '', True),
            ('Gars/Barley', '', False),
            ('Gluten', '', False),
            ('Gluten Feed 20', '', False),
            ('Gluten Feed 60', '', False),
            ('Grower Concentrate', '', False),
            ('Hawerhooi & Kaf/Oat Hay & Chaff', '', False),
            ('Hawerhooi/Oat Hay', '', False),
            ('Hawerkuilvoer', '', False),
            ('Hominy Chop', '', False),
            ('Hondepille/Dog pellets', '', False),
            ('Hondepille/Dog pellets - Trusty', '', False),
            ('Hooi/Hay', '', False),
            ('Hybro Starter', '', False),
            ('Hybro Terminal', '', False),
            ('Kalf Starter', '', False),
            ('Kalk Grof/Lime Gritt', '', False),
            ('Kalk/Lime', '', False),
            ('Kalk/Lime - Lsales', '', False),
            ('Karkasmeel/Carcass Meal', '', False),
            ('Katoen Oliekoek/Cotton Oilcake', '', False),
            ('Koring/Wheat', '', False),
        )
        for title, description, hazardous in sampletypes:
            id = folder.generateUniqueId('SampleType')
            folder.invokeFactory(id = id, type_name = 'SampleType')
            obj = folder[id]
            obj.edit(title = title,
                     description = description,
                     Hazardous = hazardous)
            obj.processForm()

    def CreateCalculationObjects(self, calcs):
        if not hasattr(self, 'calculations'):
            self.calculations = {'':None}
        folder = self.context.bika_setup.bika_calculations
        for title, CalculationDescription, DependentServices, InterimFields, Formula in calcs:
            calc_id = folder.generateUniqueId('Calculation')
            folder.invokeFactory(id = calc_id, type_name = 'Calculation')
            obj = folder[calc_id]
            obj.edit(title = title,
                      description = CalculationDescription,
                      DependentServices = [self.service_objs[a] for a in DependentServices],
                      InterimFields = InterimFields,
                      Formula = Formula)
            obj.processForm()
            obj.reindexObject()
            self.calculations[title] = obj.UID()

    def Calculations1(self):
        calcs = (
            ('Titration',
             'Titration Standard',
             [],
             [{'keyword':'TV', 'title':'Titr Vol', 'type':'int', 'value':0, 'unit':'g'},
              {'keyword':'TF', 'title':'Titr Fact', 'type':'int', 'value':0, 'unit':''}],
             '%(TV)f * %(TF)f',
             ),
            ('Weight Loss',
             'Weight loss as % moisture',
             [],
             [{'keyword':'GM', 'title':'Gross Mass', 'type':'int', 'value':0, 'unit':'g'},
              {'keyword':'NM', 'title':'Nett Mass', 'type':'int', 'value':0, 'unit':'g'},
              {'keyword':'VM', 'title':'Vessel Mass', 'type':'int', 'value':0, 'unit':'g'}],
             '( %(GM)f - %(NM)f ) / ( %(GM)f - %(VM)f ) * 100',
             ),
            ('Weight Loss (tare)',
             'Weight loss (tare) as % moisture',
             [],
             [{'keyword':'SM', 'title':'Sample Mass', 'type':'int', 'value':0, 'unit':'g'},
              {'keyword':'NM', 'title':'Nett Mass', 'type':'int', 'value':0, 'unit':'g'},
              {'keyword':'VM', 'title':'Vessel Mass', 'type':'int', 'value':0, 'unit':'g'}],
             '(( %(VM)f + %(SM)f - %(NM)f ) / %(SM)f ) * 100',
             ),
            ('Residual Weight',
             'Residual Weight as % ash',
             [],
             [{'keyword':'GM', 'title':'Gross Mass', 'type':'int', 'value':0, 'unit':'g'},
              {'keyword':'NM', 'title':'Nett Mass', 'type':'int', 'value':0, 'unit':'g'},
              {'keyword':'VM', 'title':'Vessel Mass', 'type':'int', 'value':0, 'unit':'g'}],
             '(( %(NM)f - %(VM)f ) / ( %(GM)f - %(VM)f )) * 100',
             ),
            ('Residual Weight (tare)',
             'Residual Weight (tare) as % ash',
             [],
             [{'keyword':'SM', 'title':'Sample Mass', 'type':'int', 'value':0, 'unit':'g'},
              {'keyword':'NM', 'title':'Nett Mass', 'type':'int', 'value':0, 'unit':'g'},
              {'keyword':'VM', 'title':'Vessel Mass', 'type':'int', 'value':0, 'unit':'g'}],
             '(( %(NM)f - %(VM)f ) / %(SM)f ) * 100',
             ),
        )
        self.CreateCalculationObjects(calcs)

    def Calculations2(self):
        calcs = (
            ('Dry Matter',
             'Percentage dry matter. Dependent on Moisture Analysis',
             ['Moist'],
             [],
             "100 - %(Moist)f",
             ),
            ('Apparent Metabolizable Energy',
             'AME used for poultry feed',
             ['CP', 'EE', 'STA', 'SUG'],
             [],
             "%(CP)f + %(EE)f + %(STA)f + %(SUG)f",
             ),
            ('Metabolizable Energy',
             'ME used for ruminant feeds',
             ['CP', 'EE', 'CF', 'Ash'],
             [],
             "12 + ( %(CP)f + %(EE)f ) - %(CF)f + %(Ash)f",
             ),
            ('Non-Structural Carbohydrates',
             'NSC is used for dairy cattle',
             ['NDF', 'CP', 'EE', 'Ash'],
             [],
             "100 - ( %(NDF)f + %(CP)f + %(EE)f + %(Ash)f )",
             ),
            ('Digestible Energy',
             'DE is used for pig feeds',
             ['CP', 'EE', 'CF', 'Ash'],
             [],
             "17.38 + %(CP)f + %(EE)f - %(CF)s - %(Ash)f",
             ),
        )
        self.CreateCalculationObjects(calcs)

    def Calculations3(self):
        calcs = (
            ('Total Digestible Nutrients',
             'TDN % is used for ruminant feeds',
             ['ME'],
             [{'keyword':'tdnfact', 'title':'TDN Factor', 'type':'int', 'value':0, 'unit':'g'}],
             '%(tdnfact)f * 6.67',
            ),
        )
        self.CreateCalculationObjects(calcs)

    def AnalysisCategories(self):
        cats = (
            ('Air', 'Air description'),
            ('Biogas', 'Biogas description'),
            ('Dragon Fire', 'Dragon Fire description'),
            ('Feed & Compost', 'Feed & Compost description'),
            ('General', 'General description'),
            ('GHG', 'GHG description'),
            ('Mold', 'Mold description'),
            ('Oil', 'Oil description'),
            ('Precious Metals', 'Precious Metals description'),
            ('Soil', 'Soil description'),
            ('Water', 'Water description'),
        )

        def depgen():
            for c in range(len(cats)):
                for d in self.departments:
                    yield d
        depgen = depgen()

        self.categories = {}
        folder = self.context.bika_setup.bika_analysiscategories
        for title, descr in cats:
            cat_id = folder.generateUniqueId('AnalysisCategory')
            folder.invokeFactory(id = cat_id, type_name = 'AnalysisCategory')
            cat = folder[cat_id]
            cat.edit(title = title, description = descr, Department = depgen.next())
            cat.processForm()
            self.categories[title] = cat

    def CreateServiceObjects(self, services):
        if not hasattr(self, 'service_objs'):
            self.service_objs = {'':None}
        folder = self.context.bika_setup.bika_analysisservices
        price = '15.00'
        corporateprice = '12.00'
        for PointOfCapture, title, unit, min, max, titration_unit, accred, description, keyword, maxtime, uncertainties, instructions, dup_variation, calculation, dry_matter, cat in services:
            id = folder.generateUniqueId('AnalysisService')
            folder.invokeFactory(id = id, type_name = 'AnalysisService')
            obj = folder[id]
            obj.edit(PointOfCapture = PointOfCapture,
                     title = title,
                     description = description,
                     Unit = unit,
                     Calculation = self.calculations[calculation],
                     Price = price,
                     CorporatePrice = corporateprice,
                     VAT = '14.0',
                     Precision = 2,
                     Accredited = accred,
                     Keyword = keyword,
                     MaxTimeAllowed = maxtime,
                     Instructions = instructions,
                     DuplicateVariation = dup_variation,
                     ReportDryMatter = dry_matter)

            uc_out = []
            for item in uncertainties:
                uc_out.append({'intercept_min' : item[0], 'intercept_max' : item[1], 'errorvalue' : item[2]})

            category = None
            if self.categories.has_key(cat):
                category = self.categories[cat]

            obj.edit(Uncertainties = uc_out,
                     Category = category)
            obj.processForm()
            obj.reindexObject()
            self.service_objs[keyword] = obj.UID()

    def AnalysisServices1(self):
        services = (
            ('field', 'Temperature', 'Deg. C', 0, 99, '', False, 'Temperature at time of sample capture', 'Temp', {'minutes':0}, [], 'Simple temperature measurement', '1.00', '', False, 'General'),
            ('field', 'pH (field)', '', 2, 7, '', False, 'pH measured at sample capture', 'pHField', {'hours':2}, '', 'Instructions for ph Field', '5.00', '', False, 'General'),
            ('lab', 'Aflatoxins Total', 'mg/l', 2, 11, '', False, 'Description for Aflatoxins Total', 'Aflatox', {'hours':1}, [[0, 8, 0.4], [8, 12, 0.6], [12, 999, 0.8]], 'Instructions for Aflatoxins', '5.00', '', False, 'Biogas'),
            ('lab', 'Ash', '%', 15, 30, '', False, 'Description for total ash analysis', 'Ash', {'hours':2}, [[0, 20, 1], [20, 40, 2], [40, 999, 3]], 'Instructions for Ash', '5.00', 'Residual Weight', True, 'Mold'),
            ('lab', 'Calcium', 'mg/l', 5, 10, 'ml', False, 'Description for calcium determination', 'Ca', {'hours':3}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Calcium', '0.00', 'Titration', False, 'Water'),
            ('lab', 'Chlorides', 'mg/l', 3, 10, '', False, 'Description for Chloride analysis', 'Clide', {'hours':1}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Chlorides', '0.00', '', False, 'Water'),
            ('lab', 'Chlorine residual', 'mg/l', 2, 4, 'ml', False, 'Description for residual chlorine testing', 'Cl', {'hours':2}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Chlorine residual', '0.00', 'Titration', False, 'Oil'),
            ('lab', 'COD ', 'mg/l', 1, 99, '', False, 'Description for COD', 'COD', {'hours':3}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for COD', None, '', False, 'Soil'),
            ('lab', 'Conductivity @ 25 deg C', 'mS/m', 3, 10, '', False, 'Description for testing ', 'Conductivity', {'hours':4}, '', 'Instructions for Conductivity @ 25deg C', None, '', False, 'Soil'),
            ('lab', 'Copper', 'mg/l', 2, 6, 'ml', False, 'Description for copper as Cu', 'Cu', {'hours':6}, '', 'Instructions for Copper', None, '', False, 'Soil'),
            ('lab', 'Ether Extract', '%', 2, 6, '', False, 'Ether extract/crude fat', 'EE', {'hours':6}, '', 'Instructions for ether extract', None, '', False, 'Oil'),
            ('lab', 'Fat Crude', '%', 2, 45, '', False, 'Description for crude fat', 'FatCrude', {'hours':1}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Fat Crude', '5.00', 'Weight Loss (tare)', True, 'Mold'),
            ('lab', 'Fibre - ADF', '%', 10, 50, '', True, 'Description for fibre testing (ADF)', 'FibADF', {'hours':2}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Fibre ADF', '1.00', 'Weight Loss', True, 'Air'),
            ('lab', 'Fibre - Crude', '%', 3, 30, '', True, 'Description for crude fibre testing', 'CF', {'hours':3}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for crude fibre', '1.00', '', True, 'General'),
            ('lab', 'Fibre - NDF', '%', 3, 7, '', False, 'Description for NDF fibre', 'NDF', {'hours':4}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for NDF fibre', '0.00', 'Residual Weight (tare)', True, 'Water'),
            ('lab', 'Fluoride', 'mg/l', 2, 10, 'ml', False, 'Description for flouride', 'F', {'hours':5}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Flouride', None, '', False, 'Mold'),
            ('lab', 'Iron', 'mg/l', 5, 10, '', False, 'Description for iron as Fe', 'Fe', {'hours':1}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for iron', None, '', False, 'Biogas'),
            ('lab', 'Lignin', 'mg/l', 5, 10, '', True, 'Description for Lignin', 'Lignin', {'hours':2}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for lignin', None, 'Residual Weight', False, 'Mold'),
            ('lab', 'Magnesium', 'mg/l', 5, 10, '', False, 'Description for magnesium', 'Mg', {'hours':3}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for magnesium', None, '', False, 'General'),
            ('lab', 'Manganese', 'mg/l', 3, 11, '', False, 'Description for manganese', 'Mn', {'hours':4}, '', 'Instructions for manganese', None, '', False, 'Soil'),
            ('lab', 'Moisture', '%', 5, 35, '', False, 'Description for percentage moisture testing. The mass of the wet sample, dry sample and container are captured. The result is determined by the formula: (wet sample - dry sample) / (wet sample - container)', 'Moist', {'hours':5}, [[0, 10, 1], [10, 20, 2], [20, 30, 3], [30, 100, 4]], 'Instructions for moisture', None, 'Weight Loss', False, 'Water'),
            ('lab', 'Nitrates & Nitrites', 'mg/l', 5, 10, '', False, 'Description for nitrates and nitrites', 'N', {'hours':6}, '', 'Instructions for nitrates & nitrites', None, '', False, 'Water'),
            ('lab', 'Phosphorus', 'mg/l', 5, 10, '', False, 'Description for phosphorus testing', 'Phos', {'hours':1}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for phosphorus', '5.00', '', False, 'Air'),
            ('lab', 'pH (laboratory)', '', 2, 7, '', False, 'Laboratory method for pH', 'pH', {'hours':2}, '', 'Instructions for ph Lab', '5.00', '', False, 'Air'),
            ('lab', 'Phosphorus Total', 'mg/l', 5, 10, '', False, 'Description for total phosphorus', 'PhosTot', {'hours':3}, '', 'Instructions for total phosphorus', None, '', False, 'Mold'),
            ('lab', 'Protein - ADIP', 'mg/l', 5, 10, '', False, 'Description for ADIP protein', 'ADIPP', {'hours':3}, '', 'Instructions for protein', None, '', False, 'Soil'),
            ('lab', 'Protein - NDIP', 'mg/l', 5, 10, '', False, 'Description for NDIP protein', 'NDIPP', {'hours':4}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for NDIP protein', None, 'Titration', False, 'Mold'),
            ('lab', 'Protein (KOH Solubility)', 'mg/l', 5, 10, '', False, 'KOH solubility method for testing protein', 'KOHP', {'hours':5}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for KOH soluble protein', None, '', False, 'Water'),
            ('lab', 'Protein (Soluble) ', 'mg/l', 5, 10, '', False, 'Description for testing soluble protein', 'SP', {'hours':6}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for soluble protein', None, '', False, 'Water'),
            ('lab', 'Protein Crude', 'mg/l', 5, 10, '', False, 'Description for crude protein', 'CP', {'hours':7}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for crude protein', None, '', False, 'Water'),
            ('lab', 'Sodium', 'mg/l', 5, 10, '', False, 'Description for Na', 'Na', {'hours':8}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for sodium', None, '', False, 'Soil'),
            ('lab', 'Starch', '%', 5, 10, '', False, '', 'STA', {'days':1}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for starch', None, '', False, 'Mold'),
            ('lab', 'Sugars', '%', 5, 10, '', False, 'Total sugars as invert sugar', 'SUG', {'days':2}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for sugars', None, '', False, 'Water'),
            ('lab', 'Sulphate', 'mg/l', 5, 10, '', False, 'Description for SO4 testing', 'SO4', {'hours':4}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for sulphate', '10.00', '', False, 'Water'),
            ('lab', 'Suspended solids', 'mg/l', 5, 10, '', True, 'Suspended solid testing methods', 'SS', {'hours':2}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for suspended solids', '2.00', '', False, 'Soil'),
            ('lab', 'TDS (calculated)', 'mg/l', 5, 10, '', False, 'Description for TDS', 'CTDS', {'hours':1}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for calculated TDS', '2.00', '', False, 'Soil'),
            ('lab', 'Tot. Alkalinity (CaCO3)', 'mg/l', 5, 10, '', False, 'Description for determining the total alkalinity, or CaCO3 of a sample', 'CaCO3', {'hours':2}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for total alkalinity', '0.00', '', False, 'Mold'),
            ('lab', 'Tot. Hardness (THCaCO3)', 'mg/l', 4, 16, '', False, 'Description for testing hardness - CaCO3', 'THCaCO3', {'hours':3}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for total hardness', '0.00', '', False, 'Water'),
            ('lab', 'Urea ', 'mg/l', 2, 8, '', False, 'Description for urea testing', 'Urea', {'hours':4}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for urea', '0.00', '', False, 'Mold'),
            ('lab', 'Zinc', 'mg/l', 5, 9, '', False, 'Description for zinc testing', 'Zn', {'hours':10}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for zinc', '0.00', '', False, 'Soil'),
        )
        self.CreateServiceObjects(services)

    def AnalysisServices2(self):
        services = (
            ('lab', 'Dry Matter', '%', 5, 35, '', False, 'Description for percentage dry matter. Dependant on Moisture', 'DM', {'hours':5}, [[0, 10, 1], [10, 20, 2], [20, 30, 3], [30, 100, 4]], 'DM (%) = 100 - Moisture %', None, 'Dry Matter', False, 'Biogas'),
            ('lab', 'Apparent Metabolizable Energy', 'MJ/kg', 5, 9, '', False, 'AME used for poultry feed as no correction is made for faecal or endogenous energy losses', 'AME', {'hours':10}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'AME (MJ/kg) = 0.1551 ProteinCrude% + 0.3431 FatCrudeEtherExtraction% + 0.1669 Starch% + 0.1301 Sugars %', '0.00', 'Apparent Metabolizable Energy', True, 'General'),
            ('lab', 'Metabolizable Energy', 'MJ/kg DM', 5, 9, '', False, 'ME used for ruminant feeds', 'ME', {'hours':10}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'ME (MJ/kg DM) = 12 + [0.008 ProteinCrude + 0.023 FatCrudeEtherExtraction] - 0.018 FibreCrude + 0.012 Ash]', '0.00', 'Metabolizable Energy', True, 'General'),
            ('lab', 'Non-Structural Carbohydrates', '% DM', 5, 9, '', False, 'NSC is used for dairy cattle', 'NSC', {'hours':10}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'NSC% (DM) = 100 - [FibreNDF% + ProteinCrude% + FatCrudeEtherExtraction% + Ash%]', '0.00', 'Non-Structural Carbohydrates', False, 'General'),
            ('lab', 'Digestible Energy', 'MJ/kg', 5, 9, '', False, 'DE is used for pig feeds', 'DE', {'hours':10}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'DE MJ/kg = 17.38 + 0.105 ProteinCrude% + 0.114 FatCrudeEtherExtraction% -0.317 FibreCrude% -0.402 Ash%', '0.00', 'Digestible Energy', False, 'General'),
        )
        self.CreateServiceObjects(services)

    def AnalysisServices3(self):
        services = (
            ('lab', 'Total Digestible Nutrients', '% DM', 5, 9, '', False, 'TDN % is used for ruminant feeds', 'TDN', {'hours':10}, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'TDN% (DM) = ME MJ/kg DM * 6.67', '0.00', 'Total Digestible Nutrients', False, 'General'),
        )
        self.CreateServiceObjects(services)

    def Methods(self):
        methods = (
            ('pH measure', 'Remove bottle with storage solution, rinse electrode, blot dry. Measure pH of 4 buffer, which is pink. Adjust meter to read 4 with Cal 1 knob'),
            ('Titration', 'A titration is a method of analysis that will allow you to determine the precise endpoint of a reaction and therefore the precise quantity of reactant in the titration flask. A buret is used to deliver the second reactant to the flask and an indicator of pH Meter is used to detect the endpoint of the reaction')
        )
        folder = self.context.bika_setup.bika_methods
        for title, description in methods:
            id = folder.generateUniqueId('Method')
            folder.invokeFactory(id = id, type_name = 'Method')
            obj = folder[id]
            obj.edit(title = title, description = description)
            obj.processForm()

    def ReferenceDefinitions(self):
        self.ref_defs = {}
        services = self.service_objs
        referencedefinitions = (
            ('wine reference', 'white wine sample', False, False, ()),
            ('4g/l sugar', 'Sugar water', False, False, ()),
            ('8g/l sugar', 'Sugar water at 8g/l sugar', False, False, ()),
            ('distilled water', 'distilled water', True, False, ()),
            ('Acid reference', 'HCl 3%', False, True, ()),
            ('ME', 'Everything an ME needs', False, False, (services['Ash'], services['CP'], services['CF'], services['EE'])),
        )
        folder = self.context.bika_setup.bika_referencedefinitions
        for title, description, blank, hazardous, service_uids in referencedefinitions:
            id = folder.generateUniqueId('ReferenceDefinition')
            folder.invokeFactory(id = id, type_name = 'ReferenceDefinition')
            obj = folder[id]

            obj.edit(title = title,
                     description = description,
                     Blank = blank,
                     Hazardous = hazardous,
                     ReferenceResults = [{'uid':uid,
                                          'result':'100',
                                          'error':'5',
                                          'min':'95',
                                          'max':'105'} for uid in service_uids]
                     )
            obj.processForm()
            self.ref_defs[title] = obj

    def ReferenceManufacturers(self):
        manufacturers = (
            ('Bloggs & co', 'Manufacturers of fine products since 2008'),
        )
        folder = self.context.bika_setup.bika_referencemanufacturers
        for title, description in manufacturers:
            id = folder.generateUniqueId('ReferenceManufacturer')
            folder.invokeFactory(id = id, type_name = 'ReferenceManufacturer')
            obj = folder[id]
            obj.edit(title = title,
                     description = description)
            obj.processForm()

    def ReferenceSuppliers(self):
        referencesuppliers = (
            ('1', ' Acme Standards', 'acme@scapp.co.za', '021 6162050', '0216162192', 'Bobby', 'Smith', 'bobby', 'bobby@scapp.co.za'),
        )
        folder = self.context.referencesuppliers
        for account_nr, name, email, tel, fax, cname, csurname, cusername, cemail in referencesuppliers:
            referencesupplier_id = folder.generateUniqueId('ReferenceSupplier')
            folder.invokeFactory(id = referencesupplier_id, type_name = 'ReferenceSupplier')
            referencesupplier = folder[referencesupplier_id]
            name = name.decode('latin-1').encode('utf-8').strip()
            referencesupplier.edit(Name = name,
                                  AccountNumber = account_nr,
                                  EmailAddress = email,
                                  Phone = tel,
                                  Fax = fax)
            referencesupplier.processForm()

            cname = cname.decode('latin-1').encode('utf-8').strip()
            #XXX cusername is for logins, does it belong here?
            cusername = cusername.decode('latin-1').encode('utf-8').strip()
            csurname = csurname.decode('latin-1').encode('utf-8').strip()
            contact_id = self.context.generateUniqueId('SupplierContact')
            referencesupplier.invokeFactory(id = contact_id, type_name = 'SupplierContact')
            contact = referencesupplier[contact_id]
            contact.edit(Firstname = cname,
                         Surname = csurname,
                         PrimaryEmailAddress = cemail)
            contact.processForm()

    def ReferenceSamples(self):
        self.ref_samples = {}
        defs = self.ref_defs
        referencesamples = (
            ('wine reference', defs['wine reference'], False, False),
            ('4g/l sugar', defs['4g/l sugar'], False, False),
            ('8g/l sugar', defs['8g/l sugar'], False, False),
            ('distilled water', defs['distilled water'], False, True),
            ('Acid reference', defs['Acid reference'], True, False),
            ('ME', defs['ME'], False, False),
        )
        folder = self.context.referencesuppliers.objectValues()[0]
        for title, definition, blank, hazardous in referencesamples:
            id = folder.generateUniqueId('ReferenceSample')
            folder.invokeFactory(id = id,
                                 type_name = 'ReferenceSample')
            folder[id].edit(title = title,
                            Blank = definition.getBlank(),
                            Hazardous = definition.getHazardous(),
                            ReferenceResults = definition.getReferenceResults(),
                            ReferenceDefinition = definition.UID(),
                            )
            folder[id].processForm()
            self.ref_samples[title] = folder[id]

    def AttachmentTypes(self):
        attachments = (
            ('Spectrograph', 'Spectrograph image'),
            ('Photograph', 'Photographic image'),
        )
        folder = self.context.bika_setup.bika_attachmenttypes
        for title, descr in attachments:
            attach_id = folder.generateUniqueId('AttachmentType')
            folder.invokeFactory(id = attach_id, type_name = 'AttachmentType')
            attachment = folder[attach_id]
            attachment.edit(title = title, description = descr)
            attachment.processForm()

    def Products(self):
        folder = self.context.bika_setup.bika_labproducts
        products = (
            ('NaOH', 'N/100', '2', 'l', '56'),
            ('Gedistilleerde water', 'Eie kan', '5', 'l', '20'),
            ('Ethanol - Aangesuur (Pepsien)', '', '1', 'l', '30'),
            ('pH Buffer', 'pH 7', '500', 'ml', '35'),
            ('Iodine Indikator', 'Iotect', '100', 'g', '55'),
            ('Ethanol', '96%', '1000', 'ml', '30'),
            ('Mono Propylene Glycol', '', '1000', 'ml', '22.75'),
            ('Asetaldehied', '', '500', 'ml', '180'),
            ('TS standaard', '', '500', 'ml', '20'),
            ('Balling standaard', '18deg', '100', 'ml', '20'),
            ('N Butanol', '', '2.5', 'l', '520'),
            ('Bromo Cresol Groen', '', '5', 'g', '329'),
            ('KI', '', '500', 'g', '250'),
            ('Kalium Natrium Tartraat  (Roselt Sout)', '', '500', 'g', '180'),
            ('WL Nutrient Agar', '', '500', 'g', '245'),
            ('Wynsteen L (+) suur', '', '500', 'g', '186'),
            ('Appelsuur', 'Byvoegings by Wyn', '1', 'kg', '20'),
            ('Sitroensuur', 'Byvoegings by Wyn', '1', 'kg', '13.6'),
            ('Meta Wynsteensuur', 'Byvoegings by Wyn', '1', 'kg', '90'),
            ('Cream of Tartar (Kremetart)', 'Byvoegings by Wyn', '1', 'kg', '35'),
        )
        for title, description, volume, unit, price in products:
            id = folder.generateUniqueId('LabProduct')
            folder.invokeFactory(id = id, type_name = 'LabProduct')
            obj = folder[id]
            obj.edit(
                title = title,
                description = description,
                Volume = volume,
                Unit = unit,
                Price = price,
                VAT = '14.0')
            obj.processForm()

    def WorksheetTemplates(self):
        templates = (
            ('ME',
             ({'pos':1, 'type':'b', 'sub':self.ref_defs['ME'].UID(), 'dup':''},
              {'pos':2, 'type':'a', 'sub':'', 'dup':''},
              {'pos':3, 'type':'a', 'sub':'', 'dup':''},
              {'pos':4, 'type':'a', 'sub':'', 'dup':''},
              {'pos':5, 'type':'a', 'sub':'', 'dup':''},
              {'pos':6, 'type':'a', 'sub':'', 'dup':''}),
             (self.service_objs['Ash'],
              self.service_objs['EE'],
              self.service_objs['CF'],
              self.service_objs['CP'],
              self.service_objs['ME'])),
        )
        folder = self.context.bika_setup.bika_worksheettemplates
        for title, pos, serv  in templates:
            id = folder.generateUniqueId('WorksheetTemplate')
            folder.invokeFactory(id = id, type_name = 'WorksheetTemplate')
            obj = folder[id]
            obj.edit(title = title,
                     Layout = pos,
                     Service = serv)
            obj.processForm()

    def Prefixes(self):
        bs = getToolByName(self.context, 'bika_setup')
        bs.setPrefixes([
            {'portal_type': 'AnalysisRequest', 'prefix': 'AR-', 'padding': '2'},
            {'portal_type': 'Sample', 'prefix': 'S-', 'padding': '5'},
            {'portal_type': 'Worksheet', 'prefix': 'WS-', 'padding': '5'},
            {'portal_type': 'SupplyOrder', 'prefix': 'O-', 'padding': '4', },
            {'portal_type': 'Invoice', 'prefix': 'I-', 'padding': '4'},
            {'portal_type': 'ARImport', 'prefix': 'B-', 'padding': '4'},
            {'portal_type': 'ReferenceSample', 'prefix': 'RS-', 'padding': '4'},
            {'portal_type': 'ReferenceAnalysis', 'prefix': 'RA-', 'padding': '4'},
        ])
