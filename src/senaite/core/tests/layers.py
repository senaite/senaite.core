# -*- coding: utf-8 -*-

import transaction
from bika.lims.exportimport.load_setup_data import LoadSetupData
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import logout
from plone.testing import zope


class BaseLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        super(BaseLayer, self).setUpZope(app, configurationContext)

        # Load ZCML
        import bika.lims
        import senaite.core
        import senaite.core.listing
        import senaite.core.spotlight
        import senaite.impress
        import senaite.lims
        import Products.TextIndexNG3

        self.loadZCML(package=bika.lims)
        self.loadZCML(package=senaite.core)
        self.loadZCML(package=senaite.core.listing)
        self.loadZCML(package=senaite.core.spotlight)
        self.loadZCML(package=senaite.impress)
        self.loadZCML(package=senaite.lims)
        self.loadZCML(package=Products.TextIndexNG3)

        # Install product and call its initialize() function
        zope.installProduct(app, "bika.lims")
        zope.installProduct(app, "senaite.core")
        zope.installProduct(app, "senaite.core.listing")
        zope.installProduct(app, "senaite.core.spotlight")
        zope.installProduct(app, "senaite.impress")
        zope.installProduct(app, "senaite.lims")
        zope.installProduct(app, "Products.TextIndexNG3")

    def setUpPloneSite(self, portal):
        super(BaseLayer, self).setUpPloneSite(portal)
        applyProfile(portal, "senaite.core:default")
        transaction.commit()


class DataLayer(BaseLayer):
    """Layer including Demo Data
    """

    def setup_data_load(self, portal, request):
        login(portal.aq_parent, SITE_OWNER_NAME)  # again

        # load test data
        request.form["setupexisting"] = 1
        request.form["existing"] = "bika.lims:test"
        lsd = LoadSetupData(portal, request)
        lsd()
        logout()

    def setUpPloneSite(self, portal):
        super(DataLayer, self).setUpPloneSite(portal)
        # Install Demo Data
        self.setup_data_load(portal, portal.REQUEST)
        transaction.commit()


BASE_LAYER_FIXTURE = BaseLayer()
BASE_TESTING = FunctionalTesting(
    bases=(BASE_LAYER_FIXTURE,), name="SENAITE:BaseTesting")

DATA_LAYER_FIXTURE = DataLayer()
DATA_TESTING = FunctionalTesting(
    bases=(DATA_LAYER_FIXTURE,), name="SENAITE:DataTesting")
