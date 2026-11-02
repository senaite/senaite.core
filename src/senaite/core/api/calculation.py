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

"""Evaluate the formulas of calculations

A formula refers to the values it is calculated with by placeholders, e.g.
`[Ca] + [Mg]`. The values are bound to the formula as data, never spliced
into its text (see `evaluate_formula`).
"""

import importlib
import inspect
import math
import re

from bika.lims import api

# A placeholder of a formula: a keyword in square brackets, e.g. [Ca] or
# [Ca.LDL]
PLACEHOLDER = re.compile(r"\[([^\[\]]+)\]")

# A placeholder of the string formatting formulas were evaluated with
# before, e.g. %(context_uid)s; formulas may still use it
NAMED_PLACEHOLDER = re.compile(r"%\(([^()]+)\)[sf]")

# Characters a stored formula may hold that mean nothing to it
FORMULA_NOISE = re.compile(r"[\n\t\r]")


def getGlobals(imports=None, **kwargs):
    """Return the globals dictionary for the formula calculation
    """
    # Default globals
    globs = {
        "__builtins__": None,
        "all": all,
        "any": any,
        "bool": bool,
        "chr": chr,
        "cmp": cmp,
        "complex": complex,
        "divmod": divmod,
        "enumerate": enumerate,
        "float": float,
        "format": format,
        "frozenset": frozenset,
        "hex": hex,
        "int": int,
        "len": len,
        "list": list,
        "long": long,
        "math": math,
        "max": max,
        "min": min,
        "oct": oct,
        "ord": ord,
        "pow": pow,
        "range": range,
        "reversed": reversed,
        "round": round,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "xrange": xrange,
    }
    # Update with keyword arguments
    globs.update(kwargs)
    # Update with additional Python libraries
    imports = imports or []
    for imp in imports:
        mod = imp["module"]
        func = imp["function"]
        member = getModuleMember(mod, func)
        if member is None:
            raise ImportError(
                "Could not find member {} of module {}".format(
                    func, mod))
        globs[func] = member
    return globs


def getModuleMember(dotted_name, member):
    """Get the member object of a module.

    :param dotted_name: The dotted name of the module, e.g. `scipy.special`
    :type dotted_name: string
    :param member: The name of the member function, e.g. `gammaincinv`
    :type member: string
    :returns: member object or None
    """
    try:
        mod = importlib.import_module(dotted_name)
    except ImportError:
        return None

    members = dict(inspect.getmembers(mod))
    return members.get(member)


def bind_values(formula, values):
    """Replace the placeholders of a formula by variables

    The values never become part of the formula's text: each placeholder
    is replaced by the name of a variable, and the value is bound to that
    name. A value therefore cannot add code to the formula, whatever text
    it holds.

    :param formula: the formula, with placeholders such as `[Ca]`
    :param values: mapping of placeholder keys to their values
    :returns: tuple of the expression to evaluate and its variables
    :raises KeyError: when a placeholder has no value
    """
    names = {}
    variables = {}

    def to_variable(match):
        key = match.group(1).strip()
        if key not in values:
            raise KeyError(key)
        if key not in names:
            name = "_value{}".format(len(names))
            names[key] = name
            variables[name] = values[key]
        return names[key]

    expression = NAMED_PLACEHOLDER.sub(to_variable, formula)
    expression = PLACEHOLDER.sub(to_variable, expression)
    return expression, variables


def evaluate_formula(formula, values, imports=None):
    """Evaluate a formula with the values of its placeholders

    :param formula: the formula, with placeholders such as `[Ca]`
    :param values: mapping of placeholder keys to their values
    :param imports: the Python imports the formula may use
    :returns: the result of the formula
    """
    expression, variables = bind_values(
        FORMULA_NOISE.sub("", formula), values)
    namespace = getGlobals(imports)
    namespace.update(variables)
    return eval(expression, namespace)


def unquote(text):
    """The text without the quotes a test value may be written in
    """
    if len(text) > 1 and text[0] == text[-1] and text[0] in "'\"":
        return text[1:-1]
    return text


def to_test_value(value):
    """The value of a test parameter as the formula reads it

    A number stays a number, whole numbers as integers like they were
    written; anything else is text.
    """
    if isinstance(value, (int, long, float)):
        return value
    text = api.safe_unicode(value).strip()
    for convert in (int, float):
        try:
            return convert(text)
        except ValueError:
            continue
    return unquote(text)


def calculate_formula(formula="", parameters={}, imports=None):
    result = "Failure"
    values = {key: to_test_value(value)
              for key, value in (parameters or {}).items()}

    try:
        result = evaluate_formula(formula, values, imports)
    except TypeError as e:
        # non-numeric arguments in interim mapping?
        result = "TypeError: {}".format(str(e.args[0]))
    except ZeroDivisionError as e:
        result = "Division by 0: {}".format(str(e.args[0]))
    except KeyError as e:
        result = "Key Error: {}".format(str(e.args[0]))
    except ImportError as e:
        result = "Import Error: {}".format(str(e.args[0]))
    except SyntaxError as e:
        result = "Syntax Error: {}".format(str(e.args[0]))
    except Exception as e:
        result = "Unspecified exception: {}".format(str(e.args[0]))

    return result
