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
import inspect

from bika.lims import senaiteMessageFactory as _
from senaite.core.i18n import translate
from z3c.form import validator
from zope.interface import Invalid


def _get_module_member(dotted_name, member):
    """Return the named member from a module, or None."""
    try:
        mod = importlib.import_module(dotted_name)
    except ImportError:
        return None
    return dict(inspect.getmembers(mod)).get(member)


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
        if _get_module_member(module, function) is None:
            raise Invalid(
                translate(_(
                    u"importable_function_error",
                    default=u"'${function}' not found in module '${module}'",
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
        row_validators = (importable_module(), importable_function())
        for idx, row in enumerate(value):
            for fn in row_validators:
                try:
                    fn(row)
                except Invalid as ex:
                    messages.append(
                        u"Row {}: {}".format(idx + 1, ex.args[0]))
        if messages:
            raise Invalid(u"\n".join(messages))
