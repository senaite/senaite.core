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


class BikaLIMSLayer(PloneSandboxLayer):
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


BIKA_LIMS_FIXTURE = BikaLIMSLayer()
BIKA_LIMS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BIKA_LIMS_FIXTURE,), name="BikaLIMSLayer:Functional")
