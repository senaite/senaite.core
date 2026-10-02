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
"""Pure-Python tests for senaite.core.astm.consumer.

These tests cover the envelope dispatch surface without spinning up
a Plone test layer. The intent is to catch regressions in the
boundary parser (sender name extraction, batch iteration) and to
pin behaviour across 1.x and 2.x envelope shapes.
"""

import unittest

from senaite.core.astm.consumer import PushConsumer


def envelope_2x(sender_name="HemoScreen", serial="0000-0001"):
    """A minimal 2.x-style envelope (sender is a dict)."""
    return {
        "H": [{
            "sender": {
                "name": sender_name,
                "serial": serial,
                "version": "2.4",
            },
        }],
        "P": [], "O": [], "R": [], "C": [],
        "M": [], "L": [], "Q": [],
        "metadata": {"envelope_version": "1.1", "astm": "", "hl7": ""},
    }


def envelope_1x(sender_name="Pentra XLR"):
    """A minimal 1.x-style envelope (sender as a list)."""
    return {
        "H": [{"sender": [sender_name, "SN-1", "v1"]}],
        "P": [], "O": [], "R": [],
    }


class GetSenderNameTest(unittest.TestCase):
    """`PushConsumer.get_sender_name` must accept both envelope
    shapes and never raise on malformed input.
    """

    def setUp(self):
        self.consumer = PushConsumer.__new__(PushConsumer)

    def test_returns_dict_sender_name_for_2x(self):
        self.assertEqual(
            self.consumer.get_sender_name(envelope_2x("HemoScreen")),
            "HemoScreen",
        )

    def test_returns_list_sender_name_for_1x(self):
        self.assertEqual(
            self.consumer.get_sender_name(envelope_1x("Pentra XLR")),
            "Pentra XLR",
        )

    def test_missing_header_returns_default(self):
        self.assertEqual(
            self.consumer.get_sender_name({}, default="generic"),
            "generic",
        )

    def test_non_list_header_returns_default(self):
        # 1.x payloads occasionally surfaced H as a dict. Must not crash.
        self.assertEqual(
            self.consumer.get_sender_name({"H": {"oops": True}}),
            "",
        )

    def test_empty_header_returns_default(self):
        self.assertEqual(
            self.consumer.get_sender_name({"H": []}), "")

    def test_multiple_headers_returns_default(self):
        # Ambiguous; refuse to guess. The consumer logs and falls
        # through to the generic adapter.
        self.assertEqual(
            self.consumer.get_sender_name({"H": [{}, {}]}), "")

    def test_dict_sender_without_name_returns_default(self):
        env = {"H": [{"sender": {"serial": "X"}}]}
        self.assertEqual(
            self.consumer.get_sender_name(env, default="fallback"),
            "fallback",
        )

    def test_list_sender_empty_returns_default(self):
        env = {"H": [{"sender": []}]}
        self.assertEqual(
            self.consumer.get_sender_name(env, default="fallback"),
            "fallback",
        )

    def test_sender_missing_returns_default(self):
        env = {"H": [{}]}
        self.assertEqual(self.consumer.get_sender_name(env), "")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GetSenderNameTest))
    return suite
