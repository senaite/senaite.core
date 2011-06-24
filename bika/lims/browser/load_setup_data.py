from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import logger, bikaMessageFactory as _
from zope.browser.interfaces import IBrowserView
from zope.component import getMultiAdapter
from zope.interface import implements

class LoadSetupData(BrowserView):
    implements(IBrowserView)

#    def index_html_link(self):
#        

    def __call__(self):
        logger.info("load_setup_data: Laboratory: %s" % self.Laboratory())
        logger.info("load_setup_data: Members and Groups: %s" % self.MembersAndGroups())
        logger.info("load_setup_data: Lab Contacts: %s" % self.LabContacts())
        logger.info("load_setup_data: Clients: %s" % self.Clients())
        logger.info("load_setup_data: Departments: %s" % self.Departments())
        logger.info("load_setup_data: Instruments: %s" % self.Instruments())
        logger.info("load_setup_data: Sample Points: %s" % self.SamplePoints())
        logger.info("load_setup_data: Sample Types: %s" % self.SampleTypes())
        logger.info("load_setup_data: Calculation Types: %s" % self.CalculationTypes())
        logger.info("load_setup_data: Analysis Categories: %s" % self.AnalysisCategories())
        logger.info("load_setup_data: Analysis Services: %s" % self.AnalysisServices())
        logger.info("load_setup_data: Methods: %s" % self.Methods())
        logger.info("load_setup_data: Standard Stocks: %s" % self.StandardStocks())
        logger.info("load_setup_data: Standard Suppliers: %s" % self.StandardSuppliers())
        logger.info("load_setup_data: Attachment Types: %s" % self.AttachmentTypes())
        logger.info("load_setup_data: Products: %s" % self.Products())
#        logger.info("load_setup_data: Worksheet Templates: %s" % self.WorksheetTemplates())
        logger.info("load_setup_data: Standard Manufacturers: %s" % self.StandardManufacturers())
        logger.info("load_setup_data: Prefixes: %s" % self.Prefixes())

        self.context.plone_utils.addPortalMessage(
                        _(u'Setup data loaded.'), 'info')

        plone = getMultiAdapter((self, self.request), name = "plone_portal_state").portal()
        self.request.response.redirect(plone.absolute_url())

#    # Setup client status
#    folder = context.bika_client_status
#    for title in ('Premier', 'Standard', 'Historic'):
#        id = folder.generateUniqueId('ClientStatus')
#        folder.invokeFactory(id = id, type_name = 'ClientStatus')
#        obj = folder[id]
#        obj.edit(title = title)
#
#
#    # Setup invoice prefs
#    folder = context.bika_invoice_prefs
#    for title in ('email', 'fax'):
#        id = folder.generateUniqueId('ClientInvoicePreference')
#        folder.invokeFactory(id = id, type_name = 'ClientInvoicePreference')
#        obj = folder[id]
#        obj.edit(title = title)
#
#
#    # Setup publication prefs
#    folder = context.bika_publication_prefs
#    for title in ('email', 'fax', 'file', 'pdf', 'print', 'sms'):
#        id = folder.generateUniqueId('ClientPublicationPreference')
#        folder.invokeFactory(id = id, type_name = 'ClientPublicationPreference')
#        obj = folder[id]
#        obj.edit(title = title)

    def Laboratory(self):
        name = 'Bika Laboratory'
        name = name.decode('latin-1').encode('utf-8').strip()
        self.context.bika_settings.laboratory.edit(
            Name = name,
            EmailAddress = 'lab@scapp.co.za',
            Confidence = '95',
        )

    def MembersAndGroups(self):
        pr = getToolByName(self.context, 'portal_registration')
        pg = getToolByName(self.context, 'portal_groups')
        pm = getToolByName(self.context, 'portal_membership')
        members = (
            ('labmanager', 'labmanager01', 'labmanager01', 'labmanager@scapp.co.za', 'labmanager'),
            ('labclerk', 'labclerk01', 'labclerk01', 'labclerk@scapp.co.za', 'labclerk'),
            ('labtechnician', 'labtechnician01', 'labtechnician01', 'labtechnician@scapp.co.za', 'labtechnician'),
            ('verifier', 'verifier01', 'verifier01', 'verifier@scapp.co.za', 'labtechnician'),
            ('publisher', 'publisher01', 'publisher01', 'publisher@scapp.co.za', 'labtechnician'),
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
                try:
                    pr.addMember(cusername, cusername, properties = self.context.REQUEST)
                except:
                    pass
                contact.setUsername(cusername)

                # Give contact an Owner local role on client
                pm = getToolByName(contact, 'portal_membership')
                pm.setLocalRoles(obj = contact.aq_parent, member_ids = [cusername],
                    member_role = 'Owner')

                # add user to clients group 
                group = self.context.portal_groups.getGroupById('clients')
                group.addMember(cusername)
                contact.reindexObject()

    def LabContacts(self):
        contacts = (
            ('John', 'Smith', 'john@scapp.co.za', '021 5551234', '021 5551233', '0825559910'),
            ('Mary', 'Makoeba', 'mary@scapp.co.za', '021 5551236', '021 5551233', '0835558108'),
        )
        folder = self.context.bika_settings.bika_labcontacts
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

    def Departments(self):
        # XXX Do Department and LabContact relate?
        # labcontact.department is just a string from Person.
        self.departments = []
        depts = (
            ('Microbiology', 'Microbiology department'),
            ('Chemistry', 'Analytical chemistry department'),
        )
        labcontact = self.context.bika_settings.portal_catalog(portal_type = 'LabContact')[0].getObject()
        folder = self.context.bika_settings.bika_departments
        for title, descr in depts:
            dept_id = folder.generateUniqueId('Department')
            folder.invokeFactory(id = dept_id, type_name = 'Department')
            dept = folder[dept_id]
            dept.edit(title = title,
                      DepartmentDescription = descr,
                      Manager = labcontact)
            self.departments.append(dept)

    def Instruments(self):
        folder = self.context.bika_settings.bika_instruments
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
                     InstrumentDescription = description,
                     Type = type,
                     Brand = brand,
                     Model = model,
                     SerialNo = serialno,
                     CalibrationCertificate = calibrationcertificate,
                     CalibrationExpiryDate = calibrationexpiry)

    def SamplePoints(self):
        folder = self.context.bika_settings.bika_samplepoints
        samplepoints = (
            ('Plant', 'Production point'),
            ('Bag', 'Retail sample'),
            ('Swab', 'Biomedical sample'),
            )
        for title, description in samplepoints:
            id = folder.generateUniqueId('SamplePoint')
            folder.invokeFactory(id = id, type_name = 'SamplePoint')
            obj = folder[id]
            obj.edit(title = title, SamplePointDescription = description)

    def SampleTypes(self):
        folder = self.context.bika_settings.bika_sampletypes
        sampletypes = (
            ('Aartappel/Potato', '', False),
            ('Appelpulp/Apple Pulp', '', False),
            ('Bloedmeel/Blood Meal', '', True),
            ('BR BDR Grower', '', False),
            ('BR BDR Layer Phase 1', '', False),
            ('BR BDR Layer Phase 2', '', False),
            ('BR BDR Pre Breeder', '', False),
            ('BR BDR Pre Layer', '', False),
            ('BR BDR Pre-Starter', '', False),
            ('BR BDR Starter', '', False),
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
            ('Korog/Triticale', '', True),
            ('Kragvoer', '', False),
            ('Kuilvoer droog/Silage dry', '', False),
            ('Kuilvoer nat/Silage wet', '', False),
            ('Layer Concentrate', '', True),
            ('Layer Phase 1', '', False),
            ('Layer Phase 2', '', False),
            ('Lohman Breeder', '', False),
            ('Lohman Developer', '', False),
            ('Lohman Grower', '', False),
            ('Lohman Pre-Breeder', '', False),
            ('Lohman Pre-Layer', '', False),
            ('Lohman Starter', '', False),
            ('Lupiene/Lupins', '', False),
            ('Lusern/Lucern', '', False),
            ('Medics', '', False),
            ('Melkpoeier/Milk Powder', '', False),
            ('Mielies Geel/Yellow Maize', '', False),
            ('Mielies Wit/White Maize', '', False),
            ('Milk Prod', '', False),
            ('Milk Prod 17%', '', False),
            ('Milk Prod 19%', '', False),
            ('Mono Calphos', '', False),
            ('Nulaid', '', False),
            ('Parrot Food', '', False),
            ('Pioneer 15%', '', False),
            ('Pioneer 17%', '', False),
            ('Pioneer 19%', '', False),
            ('Pullet Grower', '', False),
            ('RB Brd. Grower', '', False),
            ('RB Brd. Layer Phase 1', '', False),
            ('RB Brd. Layer Phase 2', '', False),
            ('RB Layer Phase 2', '', False),
            ('RB. Brd. Pre-breeder', '', False),
            ('RB4 Finisher', '', False),
            ('RB4 Grower', '', False),
            ('RB4 Starter', '', False),
            ('RB4 Terminal', '', False),
            ('Rog droog', '', False),
            ('Rog nat', '', False),
            ('Rotpille/ Rat Pellets', '', True),
            ('Semels/Bran', '', False),
            ('Skulp', '', False),
            ('Sog-Beer 14%', '', False),
            ('Sog-Beer 15%', '', False),
            ('Sog-Beer 17%', '', False),
            ('Sog-Beer/Sow-Boar', '', False),
            ('Soja/Soya', '', False),
            ('Sonneblom/Sunflower', '', False),
            ('Sonneblomsaad/Sunflower seed', '', False),
            ('Stof/Dust', '', False),
            ('Strooi/Straw', '', False),
            ('Suiwel', '', False),
            ('Suiwel 17%', '', False),
            ('Trout Fry Meal', '', False),
            ('Trustymeel/Meal', '', False),
            ('Tydstroom 100', '', False),
            ('Tydstroom 110', '', False),
            ('Tydstroom 120', '', False),
            ('Tydstroom 90', '', False),
            ('Varkgroei Fase 1', '', True),
            ('Varkgroei/Pig Growth', '', True),
            ('Varkvoer/Pig Feed', '', True),
            ('Vetkoek/Fat Cake', '', True),
            ('Viskos', '', False),
            ('Vismeel/Fishmeal', '', False),
            ('Vismeel/Fishmeal Imported', '', False),
            ('Vismeel/Fishmeal Local', '', False),
            ('Vismeel/Fishmeal St Helena', '', False),
            ('Voer/Feed', '', False),
            ('Volstruisaanvang/Ostrich', '', False),
            ('Volstruisafrond/Ostrich fin.', '', False),
            ('Volstruisbroei/Ostrich', '', False),
            ('Volstruisgroei/Ostrich', '', False),
            ('Volstruisonderhoud/Ostrich', '', False),
            ('Volstruispille/Ostrich Pell.', '', False),
            ('Volstruisslag/Ostrich Slaughter', '', False),
            ('Volstruisteel/Ostrich', '', False),
            ('Volvoer', '', False),
            ('Water', '', False),
            ('Wei/Whey', '', False),
        )
        for title, description, hazardous in sampletypes:
            id = folder.generateUniqueId('SampleType')
            folder.invokeFactory(id = id, type_name = 'SampleType')
            obj = folder[id]
            obj.edit(title = title,
                     SampleTypeDescription = description,
                     Hazardous = hazardous)

    def CalculationTypes(self):
        calcs = (
            ('Titration', 'Titration standard: TV * TF', 't'),
            ('Weight loss(tare)', 'Weight loss tare as % moisture: ((VM + SM - NM)/SM) * 100', 'wlt'),
            ('Weight loss', 'Weight loss as % moisture: (GM - NM)/(GM - VM) * 100', 'wl'),
            ('Residual weight(tare)', 'Residual weight(tare) as % ash: ((NM - VM)/SM) * 100', 'rwt'),
            ('Residual weight', 'Residual weight as % ash: ((NM - VM)/(GM - VM) * 100', 'rw'),
            ('Dependant calculation', 'Dependant on a number of other results', 'dep'),
        )
        self.calctypes = {}
        folder = self.context.bika_settings.bika_calculationtypes
        for title, descr, code in calcs:
            calc_id = folder.generateUniqueId('CalculationType')
            folder.invokeFactory(id = calc_id, type_name = 'CalculationType')
            calc = folder[calc_id]
            calc.edit(title = title, CalculationTypeDescription = descr,
                      CalcTypeCode = code)
            self.calctypes[code] = calc

    def AnalysisCategories(self):
        cats = (
            ('Air', 'Air'),
            ('Biogas', 'Biogas'),
            ('Dragon Fire', 'Dragon Fire'),
            ('Feed & Compost', 'Feed & Compost'),
            ('General', 'General'),
            ('GHG', 'GHG'),
            ('Mold', 'Mold'),
            ('Oil', 'Oil'),
            ('Precious Metals', 'Precious Metals'),
            ('Soil', 'Soil'),
            ('Water', 'Water'),
        )

        def depgen():
            for c in range(len(cats)):
                for d in self.departments:
                    yield d
        depgen = depgen()

        self.categories = {}
        folder = self.context.bika_settings.bika_analysiscategories
        for title, descr in cats:
            cat_id = folder.generateUniqueId('AnalysisCategory')
            folder.invokeFactory(id = cat_id, type_name = 'AnalysisCategory')
            cat = folder[cat_id]
            cat.edit(title = title, CategoryDescription = descr, Department = depgen.next())
            self.categories[title] = cat

    def AnalysisServices(self):
        self.service_objs = {}
        services = (
            ('field', 'Temperature', 'Deg. C', 0, 99, '', False, 'Temperature at time of sample capture', 'Temp', 'Tempterature', 0, [], 'Simple temperature measurement', '1.00', '', [], False, 'General'),
            ('field', 'pH (field)', '', 2, 7, '', False, 'pH measured at sample capture', 'pH', 'pH', 2, '', 'Instructions for ph Field', '5.00', '', [], False, 'General'),
            ('lab', 'Aflatoxins Total', 'mg/l', 2, 11, '', False, 'Description for Aflatoxins Total', 'Aflatox', 'Aflatoxins', 1, [[0, 8, 0.4], [8, 12, 0.6], [12, 999, 0.8]], 'Instructions for Aflatoxins', '5.00', '', [], False, 'Biogas'),
            ('lab', 'Ash', '%', 15, 30, '', False, 'Description for total ash analysis', 'Ash', 'Ash', 2, [[0, 20, 1], [20, 40, 2], [40, 999, 3]], 'Instructions for Ash', '5.00', 'rw', [], True, 'Mold'),
            ('lab', 'Calcium', 'mg/l', 5, 10, 'ml', False, 'Description for calcium determination', 'Ca', 'Calcium', 3, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Calcium', '0.00', 't', [], False, 'Water'),
            ('lab', 'Chlorides', 'mg/l', 3, 10, '', False, 'Description for Chloride analysis', 'Clide', 'Chlorides', 1, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Chlorides', '0.00', '', [], False, 'Water'),
            ('lab', 'Chlorine residual', 'mg/l', 2, 4, 'ml', False, 'Description for residual chlorine testing', 'Cl', 'Chlorine', 2, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Chlorine residual', '0.00', 't', [], False, 'Oil'),
            ('lab', 'COD ', 'mg/l', 1, 99, '', False, 'Description for COD', 'COD', 'COD', 3, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for COD', None, '', [], False, 'Soil'),
            ('lab', 'Conductivity @ 25 deg C', 'mS/m', 3, 10, '', False, 'Description for testing ', '', 'Conductivity', 4, '', 'Instructions for Conductivity @ 25deg C', None, '', [], False, 'Soil'),
            ('lab', 'Copper', 'mg/l', 2, 6, 'ml', False, 'Description for copper as Cu', 'Cu', 'Copper', 6, '', 'Instructions for Copper', None, '', [], False, 'Soil'),
            ('lab', 'Ether Extract', '%', 2, 6, '', False, 'Ether extract/crude fat', 'EE', 'FatCrudeEtherExtraction', 6, '', 'Instructions for ether extract', None, '', [], False, 'Oil'),
            ('lab', 'Fat Crude', '%', 2, 45, '', False, 'Description for crude fat', 'FatCrude', 'FatCrude', 1, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Fat Crude', '5.00', 'wlt', [], True, 'Mold'),
            ('lab', 'Fibre - ADF', '%', 10, 50, '', True, 'Description for fibre testing (ADF)', 'FibADF', 'FibreADF', 2, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Fibre ADF', '1.00', 'wl', [], True, 'Air'),
            ('lab', 'Fibre - Crude', '%', 3, 30, '', True, 'Description for crude fibre testing', 'CF', 'FibreCrude', 3, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for crude fibre', '1.00', '', [], True, 'General'),
            ('lab', 'Fibre - NDF', '%', 3, 7, '', False, 'Description for NDF fibre', 'NDF', 'FibreNDF', 4, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for NDF fibre', '0.00', 'rwt', [], True, 'Water'),
            ('lab', 'Fluoride', 'mg/l', 2, 10, 'ml', False, 'Description for flouride', 'F', 'Fluoride', 5, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for Flouride', None, '', [], False, 'Mold'),
            ('lab', 'Iron', 'mg/l', 5, 10, '', False, 'Description for iron as Fe', 'Fe', 'Iron', 1, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for iron', None, '', [], False, 'Biogas'),
            ('lab', 'Lignin', 'mg/l', 5, 10, '', True, 'Description for Lignin', 'Lignin', 'Lignin', 2, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for lignin', None, 'rw', [], False, 'Mold'),
            ('lab', 'Magnesium', 'mg/l', 5, 10, '', False, 'Description for magnesium', 'Mg', 'Magnesium', 3, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for magnesium', None, '', [], False, 'General'),
            ('lab', 'Manganese', 'mg/l', 3, 11, '', False, 'Description for manganese', 'Mn', 'Manganese', 4, '', 'Instructions for manganese', None, '', [], False, 'Soil'),
            ('lab', 'Moisture', '%', 5, 35, '', False, 'Description for percentage moisture testing. The mass of the wet sample, dry sample and container are captured. The result is determined by the formula: (wet sample - dry sample) / (wet sample - container)', 'Moist', 'Moisture', 5, [[0, 10, 1], [10, 20, 2], [20, 30, 3], [30, 100, 4]], 'Instructions for moisture', None, 'wl', [], False, 'Water'),
            ('lab', 'Dry Matter', '%', 5, 35, '', False, 'Description for percentage dry matter. Dependant on Moisture', 'DM', 'DryMatter', 5, [[0, 10, 1], [10, 20, 2], [20, 30, 3], [30, 100, 4]], 'DM (%) = 100 - Moisture %', None, 'dep', ['Moisture'], False, 'Biogas'),
            ('lab', 'Nitrates & Nitrites', 'mg/l', 5, 10, '', False, 'Description for nitrates and nitrites', 'N', 'Nitrates', 6, '', 'Instructions for nitrates & nitrites', None, '', [], False, 'Water'),
            ('lab', 'Phosphorus', 'mg/l', 5, 10, '', False, 'Description for phosphorus testing', 'Phos', 'Phosphorus', 1, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for phosphorus', '5.00', '', [], False, 'Air'),
            ('lab', 'pH (laboratory)', '', 2, 7, '', False, 'Laboratory method for pH', 'pH', 'pH', 2, '', 'Instructions for ph Lab', '5.00', '', [], False, 'Air'),
            ('lab', 'Phosphorus Total', 'mg/l', 5, 10, '', False, 'Description for total phosphorus', 'PhosTot', 'PhosphorusTotal', 3, '', 'Instructions for total phosphorus', None, '', [], False, 'Mold'),
            ('lab', 'Protein - ADIP', 'mg/l', 5, 10, '', False, 'Description for ADIP protein', '', 'ProteinADIP', 3, '', 'Instructions for protein', None, '', [], False, 'Soil'),
            ('lab', 'Protein - NDIP', 'mg/l', 5, 10, '', False, 'Description for NDIP protein', '', 'ProteinNDIP', 4, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for NDIP protein', None, 't', [], False, 'Mold'),
            ('lab', 'Protein (KOH Solubility)', 'mg/l', 5, 10, '', False, 'KOH solubility method for testing protein', '', 'ProteinKOH', 5, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for KOH soluble protein', None, '', [], False, 'Water'),
            ('lab', 'Protein (Soluble) ', 'mg/l', 5, 10, '', False, 'Description for testing soluble protein', '', 'ProteinSoluble', 6, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for soluble protein', None, '', [], False, 'Water'),
            ('lab', 'Protein Crude', 'mg/l', 5, 10, '', False, 'Description for crude protein', 'CP', 'ProteinCrude', 7, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for crude protein', None, '', [], False, 'Water'),
            ('lab', 'Sodium', 'mg/l', 5, 10, '', False, 'Description for Na', 'Na', 'Sodium', 8, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for sodium', None, '', [], False, 'Soil'),
            ('lab', 'Starch', '%', 5, 10, '', False, '', 'STA', 'Starch', 24, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for starch', None, '', [], False, 'Mold'),
            ('lab', 'Sugars', '%', 5, 10, '', False, 'Total sugars as invert sugar', 'SUG', 'Sugars', 48, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for sugars', None, '', [], False, 'Water'),
            ('lab', 'Sulphate', 'mg/l', 5, 10, '', False, 'Description for SO4 testing', 'SO4', 'Sulphate', 4, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for sulphate', '10.00', '', [], False, 'Water'),
            ('lab', 'Suspended solids', 'mg/l', 5, 10, '', True, 'Suspended solid testing methods', '', 'SuspendedSolids', 2, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for suspended solids', '2.00', '', [], False, 'Soil'),
            ('lab', 'TDS (calculated)', 'mg/l', 5, 10, '', False, 'Description for TDS', '', 'TDSCalculated', 1, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for calculated TDS', '2.00', '', [], False, 'Soil'),
            ('lab', 'Tot. Alkalinity (CaCO3)', 'mg/l', 5, 10, '', False, 'Description for determining the total alkalinity, or CaCO3 of a sample', 'CaCO3', 'TotalAlkalinityCaCO3', 2, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for total alkalinity', '0.00', '', [], False, 'Mold'),
            ('lab', 'Tot. Hardness (CaCO3)', 'mg/l', 4, 16, '', False, 'Description for testing hardness - CaCO3', '', 'TotalHardnessCaCO3', 3, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for total hardness', '0.00', '', [], False, 'Water'),
            ('lab', 'Urea ', 'mg/l', 2, 8, '', False, 'Description for urea testing', 'Urea', 'Urea', 4, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for urea', '0.00', '', [], False, 'Mold'),
            ('lab', 'Zinc', 'mg/l', 5, 9, '', False, 'Description for zinc testing', 'Zn', 'Zinc', 10, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'Instructions for zinc', '0.00', '', [], False, 'Soil'),
            ('lab', 'Apparent Metabolizable Energy', 'MJ/kg', 5, 9, '', False, 'AME used for poultry feed as no correction is made for faecal or endogenous energy losses', 'AME', 'AME', 10, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'AME (MJ/kg) = 0.1551 ProteinCrude% + 0.3431 FatCrudeEtherExtraction% + 0.1669 Starch% + 0.1301 Sugars %', '0.00', 'dep', ['ProteinCrude', 'FatCrudeEtherExtraction', 'Starch', 'Sugars'], True, 'General'),
            ('lab', 'Metabolizable Energy', 'MJ/kg DM', 5, 9, '', False, 'ME used for ruminant feeds', 'ME', 'ME', 10, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'ME (MJ/kg DM) = 12 + [0.008 ProteinCrude + 0.023 FatCrudeEtherExtraction] - 0.018 FibreCrude + 0.012 Ash]', '0.00', 'dep', ['ProteinCrude', 'FatCrudeEtherExtraction', 'FibreCrude', 'Ash'], True, 'General'),
            ('lab', 'Total Digestible Nutrients', '% DM', 5, 9, '', False, 'TDN % is used for ruminant feeds', 'TDN', 'TDN', 10, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'TDN% (DM) = ME MJ/kg DM * 6.67', '0.00', 'dep', ['ME', ], False, 'General'),
            ('lab', 'Non-Structural Carbohydrates', '% DM', 5, 9, '', False, 'NSC is used for dairy cattle', 'NSC', 'NSC', 10, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'NSC% (DM) = 100 - [FibreNDF% + ProteinCrude% + FatCrudeEtherExtraction% + Ash%]', '0.00', 'dep', ['FibreNDF', 'ProteinCrude', 'FatCrudeEtherExtraction', 'Ash'], False, 'General'),
            ('lab', 'Digestible Energy', 'MJ/kg', 5, 9, '', False, 'DE is used for pig feeds', 'DE', 'DE', 10, [[0, 5, 0.1], [5, 10, 0.2], [10, 999, 0.3]], 'DE MJ/kg = 17.38 + 0.105 ProteinCrude% + 0.114 FatCrudeEtherExtraction% -0.317 FibreCrude% -0.402 Ash%', '0.00', 'dep', ['ProteinCrude', 'FatCrudeEtherExtraction', 'FibreCrude', 'Ash'], False, 'General'),
        )
        folder = self.context.bika_settings.bika_analysisservices
        price = '15.00'
        corporateprice = '12.00'
        for PointOfCapture, title, unit, min, max, titration_unit, accred, description, instr_kw, keyword, maxhours, uncertainties, instructions, dup_variation, calctype, dependancies, dry_matter, cat in services:
            id = folder.generateUniqueId('AnalysisService')
            folder.invokeFactory(id = id, type_name = 'AnalysisService')
            obj = folder[id]
            obj.edit(PointOfCapture = PointOfCapture,
                     title = title,
                     Unit = unit,
                     Price = price,
                     CorporatePrice = corporateprice,
                     VAT = '14.0',
                     Precision = 2,
                     TitrationUnit = titration_unit,
                     Accredited = accred,
                     ServiceDescription = description,
                     InstrumentKeyword = instr_kw,
                     AnalysisKey = keyword,
                     MaxHoursAllowed = maxhours,
                     Instructions = instructions,
                     DuplicateVariation = dup_variation,
                     ReportDryMatter = dry_matter)

            uc_out = []
            for item in uncertainties:
                uc_out.append({'intercept_min' : item[0],
                               'intercept_max' : item[1],
                               'errorvalue' : item[2]})

            category = None
            if self.categories.has_key(cat):
                category = self.categories[cat]

            ctype = ''
            if self.calctypes.has_key(calctype):
                ctype = self.calctypes[calctype]

            deps = []
            for item in dependancies:
                if self.service_objs.has_key(item):
                    deps.append(self.service_objs[item])

            obj.edit(Uncertainties = uc_out,
                     CalculationType = ctype,
                     CalcDependancy = deps,
                     Category = category)
            obj.reindexObject()
            self.service_objs[keyword] = obj.UID()

    def Methods(self):
        methods = (
            ('pH measure', '<p>Remove bottle with storage solution, rinse electrode, blot dry</p><p>Measure pH of 4 buffer, which is pink</p><p>Adjust meter to read 4 with Cal 1 knob</p>'),
            ('Titration', '<p>A titration is a method of analysis that will allow you to determine the precise endpoint of a reaction and therefore the precise quantity of reactant in the titration flask. A buret is used to deliver the second reactant to the flask and an indicator of pH Meter is used to detect the endpoint of the reaction</p>')
        )
        folder = self.context.bika_settings.bika_methods
        for title, description in methods:
            id = folder.generateUniqueId('Method')
            folder.invokeFactory(id = id, type_name = 'Method')
            obj = folder[id]
            obj.edit(title = title,
                     MethodDescription = description)
#xxx            obj.create_log_entry()

    def StandardStocks(self):
        self.std_stocks = []
        standardstocks = (
            ('wine standard', 'white wine sample', False),
            ('4g/l sugar', 'Sugar water', False),
            ('8g/l sugar', 'Sugar water at 8g/l sugar', False),
            ('distilled water', 'distilled water', False),
            ('Acid standard', 'HCl 3%', True),
        )
        folder = self.context.bika_settings.bika_standardstocks
        for title, description, hazardous in standardstocks:
            id = folder.generateUniqueId('StandardStock')
            folder.invokeFactory(id = id, type_name = 'StandardStock')
            obj = folder[id]
            obj.edit(title = title,
                     StandardStockDescription = description,
                     Hazardous = hazardous)
            self.std_stocks.append(obj)

    def StandardSuppliers(self):
        standardsuppliers = (
            ('1', ' Acme Standards', 'acme@scapp.co.za', '021 6162050', '0216162192', 'Bobby', 'Smith', 'bobby', 'bobby@scapp.co.za'),
            ('2', ' Samples for Africa', 'sfa@scapp.co.za', '021 3491150', '0213491504', 'Bulelani', 'Miyama', 'bulelani', 'bulelani@scapp.co.za'),
            ('3', ' Everything Normal', 'en@scapp.co.za', '021 3443026', '0213443157', 'Meredith', 'Miller', 'meredith', 'meredith@scapp.co.za'),
        )
        folder = self.context.standardsuppliers
        for account_nr, name, email, tel, fax, cname, csurname, cusername, cemail in standardsuppliers:
            standardsupplier_id = folder.generateUniqueId('StandardSupplier')
            folder.invokeFactory(id = standardsupplier_id, type_name = 'StandardSupplier')
            standardsupplier = folder[standardsupplier_id]
            name = name.decode('latin-1').encode('utf-8').strip()
            standardsupplier.edit(Name = name,
                                  AccountNumber = account_nr,
                                  EmailAddress = email,
                                  Phone = tel,
                                  Fax = fax)

            cname = cname.decode('latin-1').encode('utf-8').strip()
            #XXX cusername is for logins, does it belong here?
            cusername = cusername.decode('latin-1').encode('utf-8').strip()
            csurname = csurname.decode('latin-1').encode('utf-8').strip()
            contact_id = self.context.generateUniqueId('SupplierContact')
            standardsupplier.invokeFactory(id = contact_id, type_name = 'SupplierContact')
            contact = standardsupplier[contact_id]
            contact.edit(Firstname = cname,
                         Surname = csurname,
                         PrimaryEmailAddress = cemail)

    def AttachmentTypes(self):
        attachments = (
            ('Spectrograph', 'Spectrograph image'),
            ('Photograph', 'Photographic image'),
        )
        folder = self.context.bika_settings.bika_attachmenttypes
        for title, descr in attachments:
            attach_id = folder.generateUniqueId('AttachmentType')
            folder.invokeFactory(id = attach_id, type_name = 'AttachmentType')
            attachment = folder[attach_id]
            attachment.edit(title = title, AttachmentTypeDescription = descr)


    def Products(self):
        folder = self.context.bika_settings.bika_labproducts
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
                ProductDescription = description,
                Volume = volume,
                Unit = unit,
                Price = price,
                VAT = '14.0')

    def WorksheetTemplates(self):
        templates = (
            ('Dry food standard', ({'pos': 1, 'type': 'b', 'sub': self.std_stocks[0]},
                                   {'pos': 2, 'type': 'c', 'sub': self.std_stocks[1]},
                                   {'pos': 3, 'type': 'a', 'sub': ''},
                                   {'pos': 4, 'type': 'a', 'sub': ''},
                                   {'pos': 5, 'type': 'd', 'sub': '3'}),
              [self.service_objs['Ash'], self.service_objs['AcidInsolubleResidue']]),
            )
        folder = self.context.bika_settings.bika_worksheettemplates
        for title, pos, serv  in templates:
            id = folder.generateUniqueId('WorksheetTemplate')
            folder.invokeFactory(id = id, type_name = 'WorksheetTemplate')
            obj = folder[id]
            obj.edit(title = title,
                     Row = pos,
                     Service = serv)

#    # Setup standard manufacturers 
    def StandardManufacturers(self):
        manufacturers = (
            ('Bloggs & co', 'Manufacturers of fine products since 2008'),
            ('Fred\'s Factory', '"We make stuff" is not just a promise!'),
            )
        folder = self.context.bika_settings.bika_standardmanufacturers
        for title, description in manufacturers:
            id = folder.generateUniqueId('StandardManufacturer')
            folder.invokeFactory(id = id, type_name = 'StandardManufacturer')
            obj = folder[id]
            obj.edit(title = title,
                     StandardManufacturerDescription = description)

    def Prefixes(self):
        bs = getToolByName(self.context, 'bika_settings')
        bs.setPrefixes([
            {'portal_type': 'AnalysisRequest', 'prefix': 'AR-', 'padding': '2'},
            {'portal_type': 'Sample', 'prefix': 'S-', 'padding': '5'},
            {'portal_type': 'Worksheet', 'prefix': 'WS-', 'padding': '5'},
            {'portal_type': 'Order', 'prefix': 'O-', 'padding': '4', },
            {'portal_type': 'Invoice', 'prefix': 'I-', 'padding': '4'},
            {'portal_type': 'ARImport', 'prefix': 'B-', 'padding': '4'},
            {'portal_type': 'StandardSample', 'prefix': 'SS-', 'padding': '4'},
            {'portal_type': 'StandardAnalysis', 'prefix': 'SA-', 'padding': '4'},
        ])
