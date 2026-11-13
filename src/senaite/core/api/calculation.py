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

A formula refers to the values it is calculated with by placeholders: the
keyword of an interim field or of a service in square brackets, e.g.
`[Ca] + [Mg]`, optionally with the suffix of a value of a dependency, e.g.
`[Ca.LDL]`. The values are bound to the formula as data, never spliced into
its text, so a value cannot add code to the formula (see `bind_values`).
"""

import ast
import importlib
import math
import re

from bika.lims import api
from RestrictedPython import compile_restricted_eval
from RestrictedPython.Eval import default_guarded_getitem
from RestrictedPython.Eval import default_guarded_getiter
from RestrictedPython.Guards import guarded_iter_unpack_sequence
from RestrictedPython.Guards import guarded_unpack_sequence
from RestrictedPython.transformer import INSPECT_ATTRIBUTES


class UnsafeFormula(ValueError):
    """A formula uses what a formula must not
    """


# A placeholder of a formula: a keyword in square brackets, e.g. [Ca] or
# [Ca.LDL]
PLACEHOLDER = re.compile(r"\[([^\[\]]+)\]")

# A placeholder of the string formatting formulas were evaluated with
# before, e.g. %(context_uid)s; formulas may still use it
NAMED_PLACEHOLDER = re.compile(r"%\(([^()]+)\)[sf]")

# Separates the keyword of a placeholder from the suffix of a value of a
# dependency, e.g. [Ca.LDL]
SUFFIX_SEPARATOR = "."

# What a formula may use besides its values and imports: no builtins of
# Python, only harmless functions and the math module
FORMULA_GLOBALS = {
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

# The errors a formula may fail with: a wrong formula, a missing value or
# import, a value of the wrong type, a division by zero
FORMULA_ERRORS = (
    ArithmeticError,
    AttributeError,
    ImportError,
    LookupError,
    NameError,
    SyntaxError,
    TypeError,
    ValueError,
)

# The text a test result shows for an error, the most specific one first
ERROR_LABELS = (
    (UnsafeFormula, "Unsafe formula"),
    (ZeroDivisionError, "Division by 0"),
    (KeyError, "Key Error"),
    (ImportError, "Import Error"),
    (SyntaxError, "Syntax Error"),
    (TypeError, "TypeError"),
)

# A formula must not reach the internals of Python objects: the way out of
# the restricted globals goes through attributes such as `__class__` or
# `__subclasses__`. Attributes starting with this are refused
PRIVATE_PREFIX = "_"

# Names starting with this are refused
DUNDER_PREFIX = "__"

# The variables a formula reads its values from: `formula_value0`, ...
VALUE_PREFIX = "formula_value"

# Attributes that lead from an object to the frames, code and globals of the
# interpreter: the ones RestrictedPython refuses, and the internals of
# functions and methods of Python 2, which it does not know
UNSAFE_ATTRIBUTES = INSPECT_ATTRIBUTES | frozenset([
    "f_lasti",
    "f_lineno",
    "func_closure",
    "func_code",
    "func_defaults",
    "func_dict",
    "func_globals",
    "gi_running",
    "im_class",
    "im_func",
    "im_self",
    "mro",
])

# Attributes of a text that may not be used: `format` reads attributes
# itself, without any check
UNSAFE_TEXT_ATTRIBUTES = ("format", "format_map")

# The values of a dependency a formula may refer to by a suffix
DEPENDENCY_SUFFIXES = (
    "RESULT", "LDL", "UDL", "LOQ", "LLOQ", "ULOQ", "BELOWLDL", "ABOVEUDL",
    "BELOWLOQ", "BELOWLLOQ", "ABOVEULOQ",
)


def unique(items):
    """The items without repetitions, in the order they come first
    """
    seen = set()
    return [item for item in items if not (item in seen or seen.add(item))]


def minify_formula(formula):
    """The formula on one line

    Line breaks and tabs become spaces; spaces within the formula, e.g. in
    a string, stay as they are.

    :param formula: the formula as it is stored
    :returns: the formula on one line
    """
    return " ".join(formula.splitlines()).replace("\t", " ")


def get_placeholders(formula):
    """The keys of the placeholders of a formula, in their order

    :param formula: the formula, e.g. `[Ca] + [Ca.LDL] + [Mg]`
    :returns: list of keys, e.g. `["Ca", "Ca.LDL", "Mg"]`
    """
    return unique(key.strip() for key in PLACEHOLDER.findall(formula))


def get_keyword(placeholder):
    """The keyword of a placeholder key, without the suffix of a value

    :param placeholder: the key of a placeholder, e.g. `Ca.LDL`
    :returns: the keyword, e.g. `Ca`
    """
    return placeholder.split(SUFFIX_SEPARATOR, 1)[0]


def get_keywords(formula):
    """The keywords of the interim fields and services a formula refers to

    :param formula: the formula, e.g. `[Ca] + [Ca.LDL] + [Mg]`
    :returns: list of keywords, e.g. `["Ca", "Mg"]`
    """
    return unique(map(get_keyword, get_placeholders(formula)))


def get_module_member(dotted_name, member):
    """The member of a module, or None

    :param dotted_name: the dotted name of the module, e.g. `scipy.special`
    :param member: the name of the member, e.g. `gammaincinv`
    :returns: the member, or None when the module or member is missing
    """
    try:
        module = importlib.import_module(dotted_name)
    except ImportError:
        return None
    return getattr(module, member, None)


def get_import(record):
    """The member of a module a calculation imports

    :param record: an import of a calculation, `{"module", "function"}`
    :returns: the member
    :raises ImportError: when the module or member is missing
    """
    module, member = record["module"], record["function"]
    found = get_module_member(module, member)
    if found is None:
        raise ImportError("Could not find member {} of module {}".format(
            member, module))
    return found


def get_globals(imports=None, **kwargs):
    """The globals a formula is evaluated with

    :param imports: the imports of a calculation, `[{"module", "function"}]`
    :param kwargs: further globals
    :returns: a new mapping of names to what they stand for
    :raises ImportError: when an import is missing
    """
    globs = dict(FORMULA_GLOBALS, **kwargs)
    for record in imports or []:
        globs[record["function"]] = get_import(record)
    return globs


def is_unsafe_attribute(name):
    """Whether a formula must not use the attribute

    :param name: the name of an attribute
    """
    return name.startswith(PRIVATE_PREFIX) or name in UNSAFE_ATTRIBUTES


def is_text(obj):
    """Whether the object is a text or a text type

    :param obj: the object
    """
    if isinstance(obj, type):
        return issubclass(obj, basestring)
    return isinstance(obj, basestring)


def get_formula_attribute(obj, name, *default):
    """The attribute of an object, as a formula may read it

    The evaluation of a formula reads every attribute through this.

    :param obj: the object
    :param name: the name of the attribute
    :param default: what to return when the object has no such attribute
    :raises UnsafeFormula: when a formula must not use the attribute
    """
    if is_unsafe_attribute(name):
        raise UnsafeFormula("A formula must not use {}".format(name))
    if name in UNSAFE_TEXT_ATTRIBUTES and is_text(obj):
        raise UnsafeFormula("A formula must not use {}".format(name))
    return getattr(obj, name, *default)


def apply_function(function, *args, **kwargs):
    """Call a function with the arguments a formula unpacked
    """
    return function(*args, **kwargs)


# The guards RestrictedPython calls in the code of a formula
FORMULA_GUARDS = {
    "_apply_": apply_function,
    "_getattr_": get_formula_attribute,
    "_getitem_": default_guarded_getitem,
    "_getiter_": default_guarded_getiter,
    "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
    "_unpack_sequence_": guarded_unpack_sequence,
}


def get_unsafe_name(node):
    """The name a node of a formula must not use, or None

    :param node: a node of the syntax tree of a formula
    :returns: the attribute or name, or None when the node is fine
    """
    if isinstance(node, ast.Attribute):
        if is_unsafe_attribute(node.attr):
            return node.attr
    elif isinstance(node, ast.Name):
        if node.id.startswith(DUNDER_PREFIX):
            return node.id
    return None


def check_expression(expression):
    """Refuse an expression that reaches the internals of Python objects

    :param expression: a Python expression, e.g. a formula with its values
        bound to variables (see `bind_values`)
    :raises SyntaxError: when the expression is not valid Python
    :raises UnsafeFormula: when the expression uses a private attribute or
        a dunder name
    """
    tree = ast.parse(expression, mode="eval")
    for node in ast.walk(tree):
        name = get_unsafe_name(node)
        if name:
            raise UnsafeFormula(
                "A formula must not use {}".format(name))


def check_formula(formula):
    """Refuse a formula that reaches the internals of Python objects

    :param formula: the formula, with placeholders such as `[Ca]`
    :raises SyntaxError: when the formula is not valid
    :raises UnsafeFormula: when the formula uses a private attribute or a
        dunder name
    """
    expression = minify_formula(formula)
    expression = NAMED_PLACEHOLDER.sub(VALUE_PREFIX, expression)
    expression = PLACEHOLDER.sub(VALUE_PREFIX, expression)
    check_expression(expression)


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
            name = "{}{}".format(VALUE_PREFIX, len(names))
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
    :param imports: the imports of the calculation the formula may use
    :returns: the result of the formula
    :raises: one of `FORMULA_ERRORS` when the formula fails, among them
        `UnsafeFormula` for a formula that reaches the internals of Python
        objects
    """
    expression, variables = bind_values(minify_formula(formula), values)
    check_expression(expression)
    # compile the formula so that every attribute, item and iteration goes
    # through a guard, which refuses what the check above cannot see
    compiled = compile_restricted_eval(expression)
    if compiled.errors:
        raise UnsafeFormula("; ".join(compiled.errors))
    namespace = get_globals(imports, **FORMULA_GUARDS)
    namespace.update(variables)
    return eval(compiled.code, namespace)


def get_interim_value(interim):
    """The value of an interim field as a formula reads it

    :param interim: an interim field, `{"keyword", "value", "result_type"}`
    :returns: a number, a text for an interim of a string type, or None
        when the interim has no value
    :raises ValueError: when the value of a numeric interim is no number
    """
    value = interim.get("value", "")
    if value == "":
        return None
    if api.is_floatable(value):
        return float(value)
    if interim.get("result_type"):
        return api.safe_unicode(value)
    raise ValueError("The value of {} is not a number".format(
        interim.get("keyword")))


def get_dependency_values(dependency, result):
    """The values of a dependency a formula may refer to

    A formula refers to the result of a dependency by its keyword, e.g.
    `[Ca]`, and to its limits by a suffix, e.g. `[Ca.LDL]`.

    :param dependency: the analysis the formula depends on
    :param result: the result of the dependency, as the formula reads it
    :returns: mapping of placeholder keys to their values
    """
    lloq = api.to_float(dependency.getLowerLimitOfQuantification(), 0.0)
    below_loq = int(dependency.isBelowLimitOfQuantification())
    suffixes = {
        "RESULT": result,
        "LDL": api.to_float(dependency.getLowerDetectionLimit(), 0.0),
        "UDL": api.to_float(dependency.getUpperDetectionLimit(), 0.0),
        "LOQ": lloq,
        "LLOQ": lloq,
        "ULOQ": api.to_float(
            dependency.getUpperLimitOfQuantification(), 0.0),
        "BELOWLDL": int(dependency.isBelowLowerDetectionLimit()),
        "ABOVEUDL": int(dependency.isAboveUpperDetectionLimit()),
        "BELOWLOQ": below_loq,
        "BELOWLLOQ": below_loq,
        "ABOVEULOQ": int(dependency.isAboveLimitOfQuantification()),
    }
    keyword = dependency.getKeyword()
    values = {SUFFIX_SEPARATOR.join([keyword, suffix]): suffixes[suffix]
              for suffix in DEPENDENCY_SUFFIXES}
    values[keyword] = result
    return values


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


def get_error_text(error):
    """The text a test result shows for an error of a formula
    """
    label = "Unspecified exception"
    for error_type, error_label in ERROR_LABELS:
        if isinstance(error, error_type):
            label = error_label
            break
    detail = error.args[0] if error.args else ""
    return "{}: {}".format(label, detail)


def calculate_formula(formula="", parameters=None, imports=None):
    """The test result of a formula, or the text of its error

    :param formula: the formula, with placeholders such as `[Ca]`
    :param parameters: mapping of placeholder keys to the test values
    :param imports: the imports of the calculation the formula may use
    :returns: the result, or the text of the error the formula failed with
    """
    values = {key: to_test_value(value)
              for key, value in (parameters or {}).items()}
    try:
        return evaluate_formula(formula, values, imports)
    except FORMULA_ERRORS as error:
        return get_error_text(error)


# BBB: the names of the content module these helpers were moved from
getGlobals = get_globals
getModuleMember = get_module_member
