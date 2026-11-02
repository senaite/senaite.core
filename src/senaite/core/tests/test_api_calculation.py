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

from senaite.core.api.calculation import bind_values
from senaite.core.api.calculation import calculate_formula
from senaite.core.api.calculation import evaluate_formula
from senaite.core.api.calculation import to_test_value

# Values that would add code to a formula they were spliced into
INJECTIONS = [
    '"+str(len(().__class__.__bases__[0].__subclasses__()))+"',
    "x' + str(1 + 1) + 'x",
    '" if True else ""; __import__("os")',
    "__import__('os').getcwd()",
]


class BindValuesTestCase(unittest.TestCase):

    def test_placeholders_become_variables(self):
        expression, variables = bind_values("[Ca] + [Mg]",
                                            {"Ca": 1.0, "Mg": 2.0})
        self.assertEqual(expression, "_value0 + _value1")
        self.assertEqual(variables, {"_value0": 1.0, "_value1": 2.0})

    def test_a_repeated_placeholder_is_one_variable(self):
        expression, variables = bind_values("[Ca] * [Ca]", {"Ca": 3.0})
        self.assertEqual(expression, "_value0 * _value0")
        self.assertEqual(variables, {"_value0": 3.0})

    def test_dotted_and_named_placeholders(self):
        expression, variables = bind_values(
            "[Ca.LDL] + get(%(context_uid)s)",
            {"Ca.LDL": 0.5, "context_uid": "abc"})
        self.assertEqual(expression, "_value1 + get(_value0)")
        self.assertEqual(variables, {"_value0": "abc", "_value1": 0.5})

    def test_a_placeholder_without_value(self):
        self.assertRaises(KeyError, bind_values, "[Ca] + [Mg]", {"Ca": 1})


class EvaluateFormulaTestCase(unittest.TestCase):

    def test_numbers(self):
        self.assertEqual(evaluate_formula("[Ca] + [Mg]",
                                          {"Ca": 5.5, "Mg": 3.25}), 8.75)

    def test_full_precision(self):
        self.assertEqual(evaluate_formula("[a] * 1", {"a": 1.23456789}),
                         1.23456789)

    def test_a_string_value(self):
        formula = '"ok" if [var] == "example" else "no"'
        self.assertEqual(evaluate_formula(formula, {"var": "example"}), "ok")
        self.assertEqual(evaluate_formula(formula, {"var": "other"}), "no")

    def test_a_value_is_never_code(self):
        formula = '"ok" if [var] == "example" else [var]'
        for value in INJECTIONS:
            self.assertEqual(evaluate_formula(formula, {"var": value}),
                             value)

    def test_imports(self):
        imports = [{"module": "math", "function": "floor"}]
        self.assertEqual(evaluate_formula("floor([Ca] + [Mg])",
                                          {"Ca": 5.6, "Mg": 3.3}, imports),
                         8.0)

    def test_noise_is_ignored(self):
        self.assertEqual(evaluate_formula("[a]\n+\t[b]\r", {"a": 1, "b": 2}),
                         3)


class CalculateFormulaTestCase(unittest.TestCase):

    def test_test_values_keep_their_number_type(self):
        self.assertEqual(to_test_value("5"), 5)
        self.assertEqual(to_test_value("5.5"), 5.5)
        self.assertEqual(to_test_value(10), 10)
        self.assertEqual(to_test_value("'uncertain'"), u"uncertain")
        self.assertEqual(to_test_value("text"), u"text")

    def test_test_values(self):
        formula = "[Comment] if [Comment] == 'uncertain' else [Ca] + [Mg]"
        params = {"Ca": "5", "Mg": "5", "Comment": "'uncertain'"}
        self.assertEqual(calculate_formula(formula, params), "uncertain")
        params["Comment"] = "certain"
        self.assertEqual(calculate_formula(formula, params), 10)

    def test_a_test_value_is_never_code(self):
        formula = "[Comment] if [Comment] == 'x' else 'no'"
        for value in INJECTIONS:
            result = calculate_formula(formula, {"Comment": value})
            self.assertEqual(result, "no")

    def test_a_missing_value(self):
        self.assertEqual(calculate_formula("[Ca] + [Mg]", {"Ca": 1}),
                         "Key Error: Mg")
