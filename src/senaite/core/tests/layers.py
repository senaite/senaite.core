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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import transaction
from senaite.core.exportimport.load_setup_data import LoadSetupData
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
        import senaite.app.listing
        import senaite.app.spotlight
        import senaite.app.supermodel
        import senaite.impress
        import senaite.lims

        self.loadZCML(package=bika.lims)
        self.loadZCML(package=senaite.core)
        self.loadZCML(package=senaite.app.listing)
        self.loadZCML(package=senaite.app.spotlight)
        self.loadZCML(package=senaite.app.supermodel)
        self.loadZCML(package=senaite.impress)
        self.loadZCML(package=senaite.lims)

        # Install product and call its initialize() function
        zope.installProduct(app, "bika.lims")
        zope.installProduct(app, "senaite.core")
        zope.installProduct(app, "senaite.app.listing")
        zope.installProduct(app, "senaite.app.spotlight")
        zope.installProduct(app, "senaite.app.supermodel")
        zope.installProduct(app, "senaite.impress")
        zope.installProduct(app, "senaite.lims")

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
