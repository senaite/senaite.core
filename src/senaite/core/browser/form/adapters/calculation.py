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

import re
from collections import OrderedDict

from bika.lims import api
from bika.lims.api.analysisservice import get_by_keyword
from senaite.core.browser.form.adapters import EditFormAdapterBase
from senaite.core.content.calculation import ICalculationSchema
from senaite.core.content.calculation import calculate_formula
from senaite.core.validators.formula import FormulaValidator

FORMULA_RX = re.compile(r"\[[^\]]*\]")
INTERIM_KEYWORD_RX = re.compile(r"interim_fields\.(\d+)\.widgets\.keyword$")
IMPORT_MODULES_RX = re.compile(r"imports\.(\d+)\.widgets\.module$")
TEST_KEYWORDS_RX = re.compile(r"test_parameters\.(\d+)\.widgets\.keyword$")
TEST_VALUE_RX = re.compile(r"test_parameters\.(\d+)\.widgets\.value$")

FIELD_FORMULA = "form.widgets.formula"
FIELD_TEST_RESULT = "form.widgets.test_result"
FIELD_DEPENDENT_SERVICES = "form.widgets.dependent_services"
FIELD_RAW_TEST_KEYWORDS = "form.widgets.raw_test_keywords"
FIELD_TEST_KEYWORD = "form.widgets.test_parameters.{}.widgets.keyword"
FIELD_TEST_VALUE = "form.widgets.test_parameters.{}.widgets.value"
FIELD_IMPORTS_FUNC = "form.widgets.imports.{}.widgets.function"
FIELD_INTERIM_VALUE = "form.widgets.interim_fields.{}.widgets.value"


class EditForm(EditFormAdapterBase):
    """Edit form adapter for Calculation
    """

    def initialized(self, data):
        self.add_callback("body",
                          "update_test_parameters",
                          "update_test_parameters")
        self.add_callback("body",
                          "datagrid:row_added",
                          "update_form")
        self.add_callback("body",
                          "datagrid:row_removed",
                          "update_form")

        # required to update the test parameters for interims on load
        self.update_form(data)
        self.update_test_parameters(data)
        return self.data

    def modified(self, data):
        errors = self.validate_formula(data)
        if errors:
            err_msg = "; ".join([err.message for err in errors])
            self.add_error_field(FIELD_FORMULA, err_msg)
            return self.data

        # clean prev error messages if validation passed
        self.add_error_field(FIELD_FORMULA, "")
        return self.update_form(data)

    def callback(self, data):
        name = data.get("name")
        if not name:
            return
        method = getattr(self, name, None)
        if not callable(method):
            return
        return method(data)

    def update_form(self, data):
        interim_kws = self.get_interimfields_keywords(data)
        formula_kws = self.get_formula_keywords(data)
        dep_services = get_by_keyword(map(
            lambda s: s.partition(".")[0],
            [k for k in formula_kws if k not in interim_kws]))
        dep_services_uids = map(api.get_uid, dep_services)
        # NOTE: This reference field is hidden and therefore, behaves like a
        # normal `textarea` field.
        # This is why we need to pass the uids as '\n' joined string.
        # self.add_update_field(
        #     FIELD_DEPENDENT_SERVICES, {"selected": dep_services_uids})
        self.add_update_field(
            FIELD_DEPENDENT_SERVICES, "\n".join(dep_services_uids))
        self.add_update_field(
            FIELD_RAW_TEST_KEYWORDS, ",".join(formula_kws))
        return self.data

    def get_interimfields_keywords(self, data):
        items = data.get("form", {}).items()
        return [v for k, v in items if INTERIM_KEYWORD_RX.search(k)]

    def get_formula_keywords(self, data):
        formula = data.get("form").get(FIELD_FORMULA, "")
        keywords = map(lambda kw: kw.strip("[]"),
                       FORMULA_RX.findall(formula))
        # ensure keywords are unique and in the right order
        return OrderedDict.fromkeys(keywords).keys()

    def update_test_parameters(self, data):
        formula = data.get("form").get(FIELD_FORMULA, "")
        formula_kws = self.get_formula_keywords(data)
        old_params = self.get_test_parameters(data)
        new_params = {}
        for index, kw in enumerate(formula_kws):
            param_name = kw
            param_value = old_params.get(kw) or ""
            new_params.update({param_name: param_value})
            self.add_update_field(FIELD_TEST_KEYWORD.format(index), param_name)
            self.add_update_field(FIELD_TEST_VALUE.format(index), param_value)

        # recalculate and update result field
        imports = self.get_imports(data)
        result = calculate_formula(formula, new_params, imports)
        self.add_update_field(FIELD_TEST_RESULT, result)

        return self.data

    def get_test_parameters(self, data):
        form = data.get("form")
        params = {}
        for k, v in form.items():
            test_match = TEST_KEYWORDS_RX.search(k)
            if test_match:
                idx = test_match.group(1)
                value = form.get(FIELD_TEST_VALUE.format(idx))
                params.update({v: value})
        return params

    def get_imports(self, data):
        form = data.get("form")
        imports = []
        for k, v in form.items():
            module_match = IMPORT_MODULES_RX.search(k)
            if module_match:
                idx = module_match.group(1)
                imports.append({
                    "module": v,
                    "function": form.get(FIELD_IMPORTS_FUNC.format(idx)),
                })
        return imports

    def validate_formula(self, data):
        formula = data.get("form").get(FIELD_FORMULA) or ""
        fields = [{"keyword": k}
                  for k in self.get_interimfields_keywords(data)]
        validator = FormulaValidator(
            self.context, self.request, None, ICalculationSchema, None)
        return validator.validate({"formula": formula,
                                   "interim_fields": fields})
