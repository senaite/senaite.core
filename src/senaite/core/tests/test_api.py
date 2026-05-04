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

import unittest2 as unittest

from senaite.core import api
from senaite.core.tests.base import DataTestCase


class TestPortalHelpers(DataTestCase):
    """Tests for the basic portal helpers in senaite.core.api."""

    def test_get_portal_returns_site_root(self):
        portal = api.get_portal()
        self.assertEqual(portal, self.portal)

    def test_get_portal_url_is_absolute(self):
        url = api.get_portal_url()
        self.assertEqual(url, self.portal.absolute_url())
        self.assertTrue(url.startswith("http"))


class TestPictogramHelpers(DataTestCase):
    """Tests for the GHS pictogram helpers in senaite.core.api."""

    def test_get_pictogram_url_for_known_code(self):
        url = api.get_pictogram_url("GHS01")
        self.assertTrue(url.endswith("/images/ghs/GHS01.svg"))
        self.assertIn(api.get_portal_url(), url)

    def test_get_pictogram_url_for_unknown_code(self):
        self.assertEqual(api.get_pictogram_url("GHSXX"), u"")
        self.assertEqual(api.get_pictogram_url(""), u"")
        self.assertEqual(api.get_pictogram_url(None), u"")

    def test_get_warning_pictogram_url(self):
        url = api.get_warning_pictogram_url()
        self.assertTrue(url.endswith("/images/iso/W001.svg"))
        self.assertIn(api.get_portal_url(), url)

    def test_get_pictogram_for_known_code(self):
        picto = api.get_pictogram("GHS06")
        self.assertIsNotNone(picto)
        self.assertEqual(picto["code"], "GHS06")
        self.assertEqual(picto["alt"], "GHS06")
        self.assertTrue(picto["url"].endswith("/images/ghs/GHS06.svg"))
        self.assertTrue(picto["title"].startswith("GHS06"))

    def test_get_pictogram_for_unknown_code(self):
        self.assertIsNone(api.get_pictogram("GHSXX"))

    def test_get_pictogram_with_override(self):
        overrides = {"GHS01": u"Custom label"}
        picto = api.get_pictogram("GHS01", overrides=overrides)
        self.assertIn(u"Custom label", picto["title"])

    def test_get_pictograms_for_codes_not_hazardous(self):
        self.assertEqual(
            api.get_pictograms_for_codes(["GHS01"], hazardous=False), [])

    def test_get_pictograms_for_codes_empty_falls_back_to_warning(self):
        result = api.get_pictograms_for_codes([], hazardous=True)
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["code"])
        self.assertTrue(result[0]["url"].endswith("/images/iso/W001.svg"))

    def test_get_pictograms_for_codes_skips_unknown(self):
        result = api.get_pictograms_for_codes(
            ["GHS01", "GHSXX", "GHS06"], hazardous=True)
        codes = [p["code"] for p in result]
        self.assertEqual(codes, ["GHS01", "GHS06"])

    def test_get_pictograms_for_codes_accepts_none(self):
        result = api.get_pictograms_for_codes(None, hazardous=True)
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["code"])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestPortalHelpers))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestPictogramHelpers))
    return suite
