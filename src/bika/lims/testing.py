# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.exportimport.load_setup_data import LoadSetupData
from plone.app.testing import (PLONE_FIXTURE, SITE_OWNER_NAME,
                               FunctionalTesting, PloneSandboxLayer, login,
                               logout)
from plone.testing import z2


class BaseLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import bika.lims
        self.loadZCML(package=bika.lims)

        import Products.TextIndexNG3
        self.loadZCML(package=Products.TextIndexNG3)

        # Install product and call its initialize() function
        z2.installProduct(app, 'bika.lims')
        z2.installProduct(app, 'Products.TextIndexNG3')

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
