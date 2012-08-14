from Products.CMFCore.utils import getToolByName
from Testing.makerequest import makerequest
from bika.lims.browser.load_setup_data import LoadSetupData
from plone.app.testing import IntegrationTesting, FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.testing import Layer
from plone.testing import z2
import Products.ATExtensions
import Products.PloneTestCase.setup
import bika.lims
import collective.js.jqueryui
import plone.app.iterate

class BikaLIMS(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        self.loadZCML(package=Products.ATExtensions)
        self.loadZCML(package=plone.app.iterate)
        self.loadZCML(package=collective.js.jqueryui)
        self.loadZCML(package=bika.lims)

        # Required by Products.CMFPlone:plone-content
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'bika.lims')

        # Install product and call its initialize() function
        z2.installProduct(app, 'bika.lims')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'bika.lims:default')

        login(portal, TEST_USER_NAME)
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager',])
        self.request = makerequest(portal.aq_parent).REQUEST

        # initialise skins support
        portal.clearCurrentSkin()
        portal.setupCurrentSkin(self.request)
        Products.PloneTestCase.setup._placefulSetUp(portal)

        self.applyProfile(portal, 'bika.lims:default')

        self.request.form['submitted'] = 1
        self.request.form['xlsx'] = "test"
        lsd = LoadSetupData(portal, self.request)
        lsd()

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'bika.lims')

BIKA_LIMS_FIXTURE = BikaLIMS()
BIKA_LIMS_INTEGRATION_TESTING = IntegrationTesting(bases=(BIKA_LIMS_FIXTURE,), name="BikaLIMSIntegrationTesting")
BIKA_LIMS_FUNCTIONAL_TESTING = FunctionalTesting(bases=(BIKA_LIMS_FIXTURE,), name="BikaLIMSFunctionalTesting")
