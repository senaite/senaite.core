# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from bika.lims.exportimport.load_setup_data import LoadSetupData


class BaseLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import bika.lims
        self.loadZCML(package=bika.lims)

        # Install product and call its initialize() function
        z2.installProduct(app, 'bika.lims')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'bika.lims:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'bika.lims')


class DataLayer(BaseLayer):
    """Layer including Demo Data
    """

    def setup_data_load(self, portal, request):
        login(portal.aq_parent, SITE_OWNER_NAME)  # again

        # load test data
        request.form['setupexisting'] = 1
        request.form['existing'] = "bika.lims:test"
        lsd = LoadSetupData(portal, request)
        lsd()
        logout()

    def setUpPloneSite(self, portal):
        super(DataLayer, self).setUpPloneSite(portal)

        # Install Demo Data
        self.setup_data_load(portal, portal.REQUEST)


BASE_LAYER_FIXTURE = BaseLayer()
BASE_TESTING = FunctionalTesting(
    bases=(BASE_LAYER_FIXTURE,), name="SENAITE:BaseTesting")

DATA_LAYER_FIXTURE = DataLayer()
DATA_TESTING = FunctionalTesting(
    bases=(DATA_LAYER_FIXTURE,), name="SENAITE:DataTesting")
