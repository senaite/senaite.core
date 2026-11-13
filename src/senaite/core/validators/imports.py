# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import importlib

from bika.lims import senaiteMessageFactory as _
from senaite.core.api.calculation import check_member
from senaite.core.api.calculation import get_module_member
from senaite.core.api.calculation import is_allowed_module
from senaite.core.api.calculation import is_unsafe_attribute
from senaite.core.api.calculation import UnsafeFormula
from senaite.core.i18n import translate
from z3c.form import validator
from zope.interface import Invalid


def allowed_module():
    """Validate that a calculation may import from the module.

    Runs before the module is imported: importing a module runs its code.
    """
    def validate(row):
        module = (row.get("module") or "").strip()
        if not module:
            return row
        if not is_allowed_module(module):
            raise Invalid(
                translate(_(
                    u"allowed_module_error",
                    default=u"Calculations must not import from "
                            u"'${module}'. A site manager may allow a "
                            u"module in the registry of the site",
                    mapping={"module": module})))
        return row
    return validate


def public_function():
    """Validate that the function is no private or unsafe member of the
    module, e.g. one that writes files."""
    def validate(row):
        function = (row.get("function") or "").strip()
        if function and is_unsafe_attribute(function):
            raise Invalid(
                translate(_(
                    u"public_function_error",
                    default=u"Calculations must not import '${function}'",
                    mapping={"function": function})))
        return row
    return validate


def importable_module():
    """Validate that the module name can be imported."""
    def validate(row):
        module = (row.get("module") or "").strip()
        if not module:
            return row
        try:
            importlib.import_module(module)
        except ImportError:
            raise Invalid(
                translate(_(
                    u"importable_module_error",
                    default=u"Could not import module '${module}'",
                    mapping={"module": module})))
        return row
    return validate


def importable_function():
    """Validate that the function exists in the module."""
    def validate(row):
        module = (row.get("module") or "").strip()
        function = (row.get("function") or "").strip()
        if not module or not function:
            return row
        if get_module_member(module, function) is None:
            raise Invalid(
                translate(_(
                    u"importable_function_error",
                    default=u"'${function}' not found in module '${module}'",
                    mapping={"function": function, "module": module})))
        return row
    return validate


def safe_function():
    """Validate that the member is no module, and of a module an add-on
    provides, a function the module defines itself."""
    def validate(row):
        module = (row.get("module") or "").strip()
        function = (row.get("function") or "").strip()
        if not module or not function:
            return row
        try:
            check_member(module, get_module_member(module, function))
        except UnsafeFormula:
            raise Invalid(
                translate(_(
                    u"safe_function_error",
                    default=u"Calculations must not import '${function}' "
                            u"from '${module}'",
                    mapping={"function": function, "module": module})))
        return row
    return validate


class ImportsValidator(validator.SimpleFieldValidator):
    """Validate python_imports rows: check module importability and
    function membership.
    """

    def validate(self, value):
        super(ImportsValidator, self).validate(value)
        if not value:
            return
        messages = []
        # The allowlist goes first and stops a row: nothing is imported
        # for a module a calculation must not use
        row_validators = (allowed_module(), public_function(),
                          importable_module(), importable_function(),
                          safe_function())
        for idx, row in enumerate(value):
            for fn in row_validators:
                try:
                    fn(row)
                except Invalid as ex:
                    messages.append(
                        u"Row {}: {}".format(idx + 1, ex.args[0]))
                    break
        if messages:
            raise Invalid(u"\n".join(messages))
