import DateTime
from Acquisition import aq_inner
from plone.app.testing import *
from plone.testing import z2

class BikaLimsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import Products.ATExtensions
        import bika.lims
        self.loadZCML(package=Products.ATExtensions)
        self.loadZCML(package=bika.lims)
        # Required by Products.CMFPlone:plone-content
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'bika.lims')

    def setUpPloneSite(self, portal):
        z2.login(portal.aq_parent['acl_users'], SITE_OWNER_NAME)

        # Installs all the Plone stuff. Workflows etc.
        self.applyProfile(portal, 'Products.CMFPlone:plone')
        # Install portal content. Including the Members folder!
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')
        self.applyProfile(portal, 'bika.lims:default')

        # test data

        portal.clients.invokeFactory('Client', id='client_1', title="Client")
        client_1 = portal.clients.client_1
        client_1.processForm()
        client_1.invokeFactory('Contact', id='contact_1', Firstname='Contact', Surname='One', PrimaryEmailAddress="test@example.com")
        client_1.contact_1.processForm()
        client_1.reindexObject()
        portal.bika_setup.bika_departments.invokeFactory("Department", id="department_1")
        portal.bika_setup.bika_departments.department_1.processForm()
        portal.bika_setup.bika_instruments.invokeFactory("Instrument", id="instrument_1", )
        portal.bika_setup.bika_instruments.instrument_1.processForm()
        portal.bika_setup.bika_samplepoints.invokeFactory("SamplePoint", id="samplepoint_1", title="Sample Point 1")
        portal.bika_setup.bika_samplepoints.samplepoint_1.processForm()
        portal.bika_setup.bika_sampletypes.invokeFactory("SampleType", id="sampletype_1", title="Sample Type 1")
        portal.bika_setup.bika_sampletypes.sampletype_1.processForm()
        portal.bika_setup.bika_sampletypes.sampletype_1.reindexObject()
        portal.bika_setup.bika_samplepoints.samplepoint_1.reindexObject()
        calcs = portal.bika_setup.bika_calculations
        calcs.invokeFactory("Calculation", id="titration", title="Titration",
            InterimFields=[{'keyword':'TV', 'title':'Titr Vol', 'type':'int', 'value':0, 'unit':'g'},
                           {'keyword':'TF', 'title':'Titr Fact', 'type':'int', 'value':0, 'unit':''}],
            Formula="%(TV)f * %(TF)f", DependentServices=[])
        calcs.titration.processForm()
        portal.bika_setup.bika_analysiscategories.invokeFactory("AnalysisCategory", id="analysiscategory_1")
        portal.bika_setup.bika_analysiscategories.analysiscategory_1.processForm()
        services = portal.bika_setup.bika_analysisservices
        services.invokeFactory("AnalysisService", id="ash", title="Ash", Keyword="Ash")
        services.ash.processForm()
        services.invokeFactory("AnalysisService", id="fibre", title="Fibre", Keyword="Fibre")
        services.fibre.processForm()
        services.invokeFactory("AnalysisService", id="protein", title="Protein", Keyword="Protein")
        services.protein.processForm()
        services.invokeFactory("AnalysisService", id="titration", title="Titration Service", Keyword="TitrationService", Calculation = calcs.titration)
        services.titration.processForm()
        calcs.invokeFactory("Calculation", id="energy",
            Formula="s%(Ash)f * %(Fibre)f * %(Protein)f + %(TitrationService)",
            DependentServices=[services.ash.UID(),services.fibre.UID(),services.protein.UID(),services.titration.UID()])
        calcs.energy.processForm()
        services.invokeFactory("AnalysisService", id="energy", title="Energy Service", Keyword="EnergyService", Calculation = calcs.energy)
        services.energy.processForm()
        refdefs = portal.bika_setup.bika_referencedefinitions
        refdefs.invokeFactory("ReferenceDefinition", id='referencedefinition_1',
            ReferenceResults = [{'uid':services.ash.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.fibre.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.protein.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.titration.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'}])
        refdefs.referencedefinition_1.processForm()
        referencesuppliers = portal.referencesuppliers
        referencesuppliers.invokeFactory('ReferenceSupplier', id="referencesupplier_1")
        referencesupplier_1 = referencesuppliers.referencesupplier_1
        referencesupplier_1.processForm()
        referencesupplier_1.invokeFactory('ReferenceSample', id='referencesample_1',
            ReferenceDefinition=refdefs.referencedefinition_1.UID(),
            ReferenceResults = [{'uid':services.ash.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.fibre.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.protein.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.titration.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'}])
        ref_1 = referencesupplier_1.referencesample_1
        ref_1.processForm()
        ws_templates = portal.bika_setup.bika_worksheettemplates
        ws_templates.invokeFactory("WorksheetTemplate", id="worksheettemplate_1",
            Row=[{'pos':'1', 'type':'c', 'sub':ref_1.UID(), 'dup':''},
                 {'pos':'2', 'type':'a', 'sub':'', 'dup':''},
                 {'pos':'3', 'type':'a', 'sub':'', 'dup':''},
                 {'pos':'4', 'type':'a', 'sub':'', 'dup':''},
                 {'pos':'5', 'type':'a', 'sub':'', 'dup':''},
                 {'pos':'6', 'type':'d', 'sub':'', 'dup':'2'}],
            Service=[services.ash.UID(),services.fibre.UID(),services.protein.UID(),services.titration.UID()])
        client_1.invokeFactory("Sample", id = 'sample_1')
        client_1.sample_1.processForm()
        client_1.sample_1.edit(
            SamplePoint = portal.bika_setup.bika_samplepoints.samplepoint_1.UID(),
            SampleType = portal.bika_setup.bika_sampletypes.sampletype_1.UID(),
            ClientReference = 'Client Reference',
            ClientSampleID = 'Client Sample ID',
            Contact = client_1.contact_1.UID(),
            DateSampled = DateTime.DateTime())
        client_1.sample_1.reindexObject()
        client_1.invokeFactory("AnalysisRequest", id='ar_1')
        ar_1 = client_1.ar_1
        ar_1.processForm()
        ar_1.setSample(client_1.sample_1.UID())
        ar_1.setAnalyses([services.fibre.UID(), services.ash.UID(), services.titration.UID(), services.energy.UID(), services.protein.UID()],
                         prices={services.fibre.UID():'10.00', services.ash.UID():'10.00', services.titration.UID():'10.00', services.energy.UID():'10.00', services.protein.UID():'10.00'})
        client_1.invokeFactory("AnalysisRequest", id='ar_2')
        ar_2 = client_1.ar_2
        ar_2.processForm()
##        ar_2.setSample(client_1.sample_1.UID())
        ar_2.setAnalyses([services.ash.UID(), services.fibre.UID()],
                         prices={services.ash.UID():'10.00', services.fibre.UID():'10.00'})

BIKA_FIXTURE = BikaLimsLayer()
BIKA_INTEGRATION_TESTING = IntegrationTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Integration")
BIKA_FUNCTIONAL_TESTING = FunctionalTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Functional")
