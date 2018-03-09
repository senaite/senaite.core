# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.tests.base import BaseTestCase


class InstallationSuccessful(BaseTestCase):

    def test_Installation_Success(self):
        """Let's see if bika is correctly installed.
        """
        portal = self.layer['portal']

        # there are no clients, but the folder should exist
        self.assertEqual(len(portal.clients.objectValues()), 0)
