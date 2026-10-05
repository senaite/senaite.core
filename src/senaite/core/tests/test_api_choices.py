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

"""The choices string interims and analysis conditions are written in."""

import unittest

from senaite.core.api import choices


class ChoicesTestCase(unittest.TestCase):

    def test_key_and_label(self):
        self.assertEqual(
            choices.to_choices("1:Positive|2:Negative"),
            {"1": "Positive", "2": "Negative"})

    # The form most analysis conditions are written in today. Without
    # this they would start reading as their own keys, which is a
    # change to data nobody edited.
    def test_an_entry_without_a_colon_is_its_own_label(self):
        self.assertEqual(
            choices.to_choices("35 degC|37 degC"),
            {"35 degC": "35 degC", "37 degC": "37 degC"})

    def test_both_forms_in_one_string(self):
        self.assertEqual(
            choices.to_choices("1:Positive|Inconclusive"),
            {"1": "Positive", "Inconclusive": "Inconclusive"})

    # Only the first colon separates. Splitting on every one of them is
    # what used to raise on a label like this.
    def test_a_label_may_contain_a_colon(self):
        self.assertEqual(
            choices.to_choices("1:Ratio 1:2"), {"1": "Ratio 1:2"})

    def test_whitespace_around_an_entry_is_ignored(self):
        self.assertEqual(
            choices.to_choices(" 1 : Positive | 2 : Negative "),
            {"1": "Positive", "2": "Negative"})

    def test_empty_entries_are_dropped(self):
        self.assertEqual(choices.to_choices("1:Positive||"),
                         {"1": "Positive"})

    def test_nothing_parses_to_nothing(self):
        for value in ("", None, "|", "  "):
            self.assertEqual(choices.to_choices(value), {})

    def test_the_order_written_is_the_order_offered(self):
        parsed = choices.to_choices("3:Three|1:One|2:Two")
        self.assertEqual(list(parsed.keys()), ["3", "1", "2"])

    def test_options_carry_value_and_text(self):
        self.assertEqual(
            choices.to_options("1:Positive"),
            [{"value": "1", "text": "Positive"}])

    def test_a_stored_value_reads_as_its_label(self):
        self.assertEqual(
            choices.get_label("1:Positive|2:Negative", "1"), "Positive")

    # A condition stored before the key form was understood holds the
    # label itself, and has to keep reading the way it was written.
    def test_a_value_that_is_not_a_key_is_left_alone(self):
        self.assertEqual(
            choices.get_label("35 degC|37 degC", "37 degC"), "37 degC")
        self.assertEqual(choices.get_label("", "whatever"), "whatever")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ChoicesTestCase))
    return suite
