# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.

import unittest

from bika.lims.utils import format_currency_symbol
from zope.i18n.locales import locales


class TestFormatCurrencySymbol(unittest.TestCase):

    def test_returns_plain_symbols_unchanged(self):
        self.assertEqual(format_currency_symbol(u"US$"), u"US$")
        self.assertEqual(format_currency_symbol(u"€"), u"€")
        self.assertEqual(format_currency_symbol("$"), "$")

    def test_returns_plural_branch_of_choice_pattern(self):
        # The locale data of the Indian Rupee stores a CLDR choice
        # pattern instead of a plain symbol
        symbol = format_currency_symbol(u"=0#Rs.|1#Re.|1<Rs.")
        self.assertEqual(symbol, u"Rs.")

    def test_returns_inr_locale_symbol(self):
        currency = locales.getLocale("en").numbers.currencies["INR"]
        self.assertEqual(format_currency_symbol(currency.symbol), u"Rs.")

    def test_returns_empty_and_missing_symbols_unchanged(self):
        self.assertEqual(format_currency_symbol(""), "")
        self.assertEqual(format_currency_symbol(None), None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFormatCurrencySymbol))
    return suite
