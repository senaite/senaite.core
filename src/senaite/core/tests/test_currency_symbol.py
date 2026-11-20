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

import unittest

from bika.lims.config import CURRENCIES
from senaite.core.i18n import get_currency_symbol
from zope.i18n.locales import locales


class TestGetCurrencySymbol(unittest.TestCase):

    def test_returns_override_for_inr(self):
        self.assertEqual(get_currency_symbol("INR"), u"\u20b9")

    def test_returns_locale_symbol(self):
        currency = locales.getLocale("en").numbers.currencies["EUR"]
        self.assertEqual(get_currency_symbol("EUR"), currency.symbol)
        self.assertEqual(get_currency_symbol("EUR"), u"\u20ac")

    def test_currencies_list_uses_override(self):
        self.assertIn(u"(\u20b9)", CURRENCIES.getValue("INR"))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetCurrencySymbol))
    return suite
