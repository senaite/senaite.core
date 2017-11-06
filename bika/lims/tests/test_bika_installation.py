# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims.testing import BIKA_LIMS_FUNCTIONAL_TESTING
from bika.lims.tests.base import BikaFunctionalTestCase


class InstallationSuccessful(BikaFunctionalTestCase):
    layer = BIKA_LIMS_FUNCTIONAL_TESTING

    def test_Installation_Success(self):
        """Let's see if bika is correctly installed.
        """
        portal = self.layer['portal']

        # there are no clients, but the folder should exist
        self.assertEqual(len(portal.clients.objectValues()), 0)
