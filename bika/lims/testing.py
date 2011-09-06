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
        # Installs all the Plone stuff. Workflows etc.
        self.applyProfile(portal, 'Products.CMFPlone:plone')
        # Install portal content. Including the Members folder!
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')

        self.applyProfile(portal, 'bika.lims:default')

BIKA_FIXTURE = BikaLimsLayer()
BIKA_INTEGRATION_TESTING = IntegrationTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Integration")
BIKA_FUNCTIONAL_TESTING = FunctionalTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Functional")
