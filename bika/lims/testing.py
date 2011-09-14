import DateTime
from Acquisition import aq_inner
from plone.app.testing import *
from plone.testing import z2

class BikaLimsLayer(PloneSandboxLayer):

#    defaultBases = (PLONE_FIXTURE,)

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

        portal.TEST_MODE = True

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

        portal.bika_setup.bika_departments.invokeFactory("Department", id="department_1")
        portal.bika_setup.bika_departments.department_1.processForm()
        portal.bika_setup.bika_instruments.invokeFactory("Instrument", id="instrument_1", )
        portal.bika_setup.bika_instruments.instrument_1.processForm()
        portal.bika_setup.bika_samplepoints.invokeFactory("SamplePoint", id="samplepoint_1", title="Sample Point 1")
        portal.bika_setup.bika_samplepoints.samplepoint_1.processForm()
        portal.bika_setup.bika_sampletypes.invokeFactory("SampleType", id="sampletype_1", title="Sample Type 1")
        portal.bika_setup.bika_sampletypes.sampletype_1.processForm()
        portal.bika_setup.bika_analysiscategories.invokeFactory("AnalysisCategory", id="analysiscategory_1")
        portal.bika_setup.bika_analysiscategories.analysiscategory_1.processForm()

        calcs = portal.bika_setup.bika_calculations
        calcs.invokeFactory("Calculation", id="titration", title="Titration",
                            InterimFields=[{'keyword':'TV', 'title':'Titr Vol', 'type':'int', 'value':0, 'unit':'g'},
                                           {'keyword':'TF', 'title':'Titr Fact', 'type':'int', 'value':0, 'unit':''}],
                            Formula="%(TV)f * %(TF)f", DependentServices=[])
        calcs.titration.processForm()
        calcs.invokeFactory("Calculation", id="residual_weight", title="Residual Weight",
                            InterimFields=[{'keyword':'GM', 'title':'Gross Mass', 'type':'int', 'value':0, 'unit':'g'},
                                           {'keyword':'NM', 'title':'Nett Mass', 'type':'int', 'value':0, 'unit':'g'},
                                           {'keyword':'VM', 'title':'Vessel Mass', 'type':'int', 'value':0, 'unit':'g'}],
                            Formula="(( %(NM)f - %(VM)f ) / ( %(GM)f - %(VM)f )) * 100",
                            DependentServices=[])
        calcs.residual_weight.processForm()
        services = portal.bika_setup.bika_analysisservices
        services.invokeFactory("AnalysisService", id="ash", title="Ash", Keyword="Ash", Calculation=calcs.residual_weight.UID())
        services.ash.processForm()
        services.invokeFactory("AnalysisService", id="ee", title="Ether Extract", Keyword="EE")
        services.ee.processForm()
        services.invokeFactory("AnalysisService", id="cf", title="Fibre Crude", Keyword="CF")
        services.cf.processForm()
        services.invokeFactory("AnalysisService", id="cp", title="Protein Crude", Keyword="CP")
        services.cp.processForm()
        services.invokeFactory("AnalysisService", id="titration", title="Titration", Keyword="titration", Calculation=calcs.titration.UID())
        services.cp.processForm()
        calcs.invokeFactory("Calculation", id="me", title="Metabolizable Energy",
                            DependentServices=[services.cp.UID(), services.ee, services.ash, services.cf],
                            Formula="12 + ( %(CP)f + %(EE)f ) - %(CF)f + %(Ash)f",
                            InterimFields=[])
        calcs.me.processForm()
        services.invokeFactory("AnalysisService", id="me", title="Metabolizable Energy", Keyword="ME", Calculation=calcs.me.UID())
        services.me.processForm()

        defs = portal.bika_setup.bika_referencedefinitions
        defs.invokeFactory("ReferenceDefinition", id='me',
            ReferenceResults = [{'uid':services.ash.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.cp.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.cf.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.ee.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'}])
        defs.me.processForm()

        suppliers = portal.referencesuppliers
        suppliers.invokeFactory('ReferenceSupplier', id="supplier_1")
        suppliers.supplier_1.processForm()
        suppliers.supplier_1.invokeFactory('ReferenceSample', id='me_reference',
            ReferenceDefinition=defs.me.UID(),
            ReferenceResults = [{'uid':services.ash.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.cp.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.cf.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'},
                                {'uid':services.ee.UID(), 'result':'100', 'error':'5', 'min':'95', 'max':'105'}])
        me_reference = suppliers.supplier_1.me_reference
        me_reference.processForm()

        ws_templates = portal.bika_setup.bika_worksheettemplates
        ws_templates.invokeFactory("WorksheetTemplate", id="me",
            Layout=[{'pos':'1', 'type':'c', 'sub':me_reference, 'dup':''},
                 {'pos':'2', 'type':'a', 'sub':'', 'dup':''},
                 {'pos':'3', 'type':'a', 'sub':'', 'dup':''},
                 {'pos':'4', 'type':'a', 'sub':'', 'dup':''},
                 {'pos':'5', 'type':'a', 'sub':'', 'dup':''},
                 {'pos':'6', 'type':'d', 'sub':'', 'dup':'2'}],
            Service=[services.ash.UID(),services.ee.UID(),services.cp.UID(),services.cf.UID()])

        client_1.invokeFactory("Sample", id='sample_1')
        client_1.sample_1.edit(
            SampleID = "sample_1",
            DateSampled = DateTime.DateTime(),
            SamplePoint = "Sample Point 1",
            SampleType = "Sample Type 1",
            ClientReference = 'Client Reference 1',
            ClientSampleID = 'Client Sample ID 1',
            Contact = client_1.contact_1.UID(),
            )
        client_1.sample_1.processForm()
        client_1.invokeFactory("AnalysisRequest", id='ar_1')
        client_1.ar_1.processForm()
        client_1.ar_1.setSample(client_1.sample_1)
        client_1.ar_1.setAnalyses([services.ash.UID(), services.cp.UID(), services.cf.UID(), services.ee.UID(), services.me.UID()],
                                  prices={services.ash.UID():'10.00', services.cp.UID():'10.00', services.cf.UID():'10.00', services.ee.UID():'10.00', services.me.UID():'10.00'})
        client_1.invokeFactory("Sample", id='sample_2')
        client_1.sample_2.edit(
            SampleID = "sample_2",
            DateSampled = DateTime.DateTime(),
            SamplePoint = "Sample Point 1",
            SampleType = "Sample Type 1",
            ClientReference = 'Client Reference 2',
            ClientSampleID = 'Client Sample ID 2',
            Contact = client_1.contact_1.UID(),
            )
        client_1.sample_2.processForm()
        client_1.invokeFactory("AnalysisRequest", id='ar_2')
        client_1.ar_2.processForm()
        client_1.ar_2.setSample(client_1.sample_2)
        client_1.ar_2.setAnalyses([services.titration.UID(), services.ash.UID(), services.cp.UID(), services.cf.UID(), services.ee.UID(), services.me.UID()],
                                  prices={services.titration.UID():'10.00', services.ash.UID():'10.00', services.cp.UID():'10.00', services.cf.UID():'10.00', services.ee.UID():'10.00', services.me.UID():'10.00'})


BIKA_FIXTURE = BikaLimsLayer()
BIKA_INTEGRATION_TESTING = IntegrationTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Integration")
BIKA_FUNCTIONAL_TESTING = FunctionalTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Functional")
