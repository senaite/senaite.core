from Acquisition import aq_inner
from Testing.makerequest import makerequest
from bika.lims.browser.load_setup_data import LoadSetupData
from plone.app.testing import *
from plone.testing import z2
import DateTime
import Products.ATExtensions
import Products.PloneTestCase.setup
import bika.lims
import os
import plone.app.iterate
import sys

class BikaLimsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        self.loadZCML(package=Products.ATExtensions)
        self.loadZCML(package=plone.app.iterate)
        self.loadZCML(package=bika.lims)
        # Required by Products.CMFPlone:plone-content
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'bika.lims')

    def setUpPloneSite(self, portal):

        login(portal, TEST_USER_NAME)
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager',])

        request = makerequest(portal.aq_parent).REQUEST

        # initialise skins support
        portal.clearCurrentSkin()
        portal.setupCurrentSkin(request)
        Products.PloneTestCase.setup._placefulSetUp(portal)

        # Installs all the Plone stuff. Workflows etc.
        self.applyProfile(portal, 'Products.CMFPlone:plone')
        # Install portal content. Including the Members folder!
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')
        self.applyProfile(portal, 'plone.app.iterate:plone.app.iterate')
        self.applyProfile(portal, 'bika.lims:default')

        xlsx = open(os.path.join(os.path.split(__file__)[0],
                                 "tests","_test.xlsx"))

        request.form['submitted'] = 1
        request.form['xlsx'] = xlsx

        lsd = LoadSetupData(portal, request)
        lsd()


BIKA_FIXTURE = BikaLimsLayer()
BIKA_INTEGRATION_TESTING = IntegrationTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Integration")
BIKA_FUNCTIONAL_TESTING = FunctionalTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Functional")
