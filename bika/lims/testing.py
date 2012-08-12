from Acquisition import aq_inner
from Testing.makerequest import makerequest
from bika.lims.browser.load_setup_data import LoadSetupData
from bika.lims.setuphandlers import setupVarious
from plone.app.testing import *
from plone.testing import z2
import DateTime
import Products.ATExtensions
import Products.PloneTestCase.setup
import bika.lims
import plone.app.collection
import os
import plone.app.iterate
import collective.js.jqueryui
import sys

class BikaLimsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        self.loadZCML(package=Products.ATExtensions)
        self.loadZCML(package=plone.app.iterate)
        self.loadZCML(package=collective.js.jqueryui)
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

        self.applyProfile(portal, 'Products.CMFPlone:plone')
        self.applyProfile(portal, 'Products.CMFPlone:dependencies')
        self.applyProfile(portal, 'Products.CMFPlone:plone-content')
        self.applyProfile(portal, 'Products.CMFPlone:testfixture')
        self.applyProfile(portal, 'plone.app.iterate:plone.app.iterate')
        self.applyProfile(portal, 'collective.js.jqueryui:default')
        self.applyProfile(portal, 'bika.lims:default')

        request.form['submitted'] = 1
        request.form['xlsx'] = "test"

        lsd = LoadSetupData(portal, request)
        lsd()

BIKA_FIXTURE = BikaLimsLayer()
BIKA_INTEGRATION_TESTING = IntegrationTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Integration")
BIKA_FUNCTIONAL_TESTING = FunctionalTesting(bases=(BIKA_FIXTURE,), name="BikaLimsLayer:Functional")
