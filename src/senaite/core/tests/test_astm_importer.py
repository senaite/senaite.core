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
"""Pure-Python tests for senaite.core.astm.importer.

Companion to test_astm_consumer: these cover the sender components the
importer reads out of the envelope, without a Plone test layer.
"""

import unittest

from senaite.core.astm.importer import ASTMImporter


def importer(header=None):
    """An importer over an envelope with the given (H)eader record"""
    data = {} if header is None else {"H": [header]}
    return ASTMImporter(data, "", None)


class GetSenderTest(unittest.TestCase):
    """`get_sender` always returns three strings

    Its callers index into the result (`get_instrument_name` and friends)
    and join it (the AutoImportLog interface), so a `None` anywhere in
    there is a traceback rather than a missing value.
    """

    def test_full_sender(self):
        sender = {"name": "XN-550", "serial": "18642", "version": "1.2"}
        result = importer({"sender": sender}).get_sender()
        self.assertEqual(result, ("XN-550", "18642", "1.2"))

    def test_null_components(self):
        """Components the analyzer does not send travel as null. `.get` with
        a default does not help: the key is there, holding `None`
        """
        sender = {"name": "XN-550", "serial": None, "version": None}
        result = importer({"sender": sender}).get_sender()
        self.assertEqual(result, ("XN-550", "", ""))

    def test_components_are_stripped(self):
        """Analyzers pad these fields to a fixed width, and the instrument
        they have to match is configured without the padding
        """
        sender = {"name": "    XN-550", "serial": "18642  ", "version": " 1 "}
        result = importer({"sender": sender}).get_sender()
        self.assertEqual(result, ("XN-550", "18642", "1"))

    def test_missing_keys(self):
        result = importer({"sender": {}}).get_sender()
        self.assertEqual(result, ("", "", ""))

    def test_null_sender(self):
        result = importer({"sender": None}).get_sender()
        self.assertEqual(result, ("", "", ""))

    def test_missing_sender(self):
        result = importer({}).get_sender()
        self.assertEqual(result, ("", "", ""))

    def test_no_header(self):
        """A message without a header used to return `None` outright"""
        result = importer().get_sender()
        self.assertEqual(result, ("", "", ""))

    def test_result_is_always_joinable(self):
        """The AutoImportLog interface is built with `", ".join(get_sender())`
        """
        sender = {"name": None, "serial": None, "version": None}
        for imp in (importer({"sender": sender}), importer()):
            self.assertEqual(", ".join(imp.get_sender()), ", , ")

    def test_accessors_do_not_raise(self):
        """They index into the tuple"""
        imp = importer()
        self.assertEqual(imp.get_instrument_name(), "")
        self.assertEqual(imp.get_instrument_serial(), "")
        self.assertEqual(imp.get_instrument_version(), "")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GetSenderTest))
    return suite
