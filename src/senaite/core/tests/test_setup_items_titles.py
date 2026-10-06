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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.core.setuphandlers import add_senaite_setup_items
from senaite.core.tests.base import BaseTestCase

LAB_NAME = "Laboratory for Applied Materials Research"


class TestSetupItemsTitles(BaseTestCase):
    """Re-running the setup handler must not rename the laboratory

    The handler resets the titles of the setup folders so that a renamed
    folder label reaches existing sites. The laboratory sits in the same
    list, but its title is the laboratory's name, entered by the lab.
    """

    def setUp(self):
        super(TestSetupItemsTitles, self).setUp()
        self.setup = api.get_senaite_setup()
        self.laboratory = self.setup.laboratory

    def test_laboratory_name_survives_a_profile_import(self):
        self.laboratory.setName(LAB_NAME)
        add_senaite_setup_items(self.portal)
        self.assertEqual(self.laboratory.getName(), LAB_NAME)

    def test_folder_titles_are_still_reset(self):
        methods = self.setup.methods
        methods.setTitle("Renamed by hand")
        add_senaite_setup_items(self.portal)
        self.assertEqual(methods.Title(), "Methods")
