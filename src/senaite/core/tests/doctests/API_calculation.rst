API Calculation
---------------

The calculation API evaluates the formulas of calculations. A formula refers
to the values it is calculated with by placeholders: the keyword of an interim
field or of a service in square brackets, e.g. `[Ca] + [Mg]`, optionally with
the suffix of a value of a dependency, e.g. `[Ca.LDL]`. The values are bound
to the formula as data and never become part of its text, so a value cannot
add code to the formula.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_calculation


Test Setup
..........

Needed Imports:

    >>> from senaite.core.api.calculation import *


Reading a formula
.................

A formula may be stored on several lines. `minify_formula` puts it on one line;
spaces within the formula, e.g. in a string, stay as they are:

    >>> minify_formula("[Ca]\n+\t[Mg]")
    '[Ca] + [Mg]'

    >>> minify_formula('"a  b" if [x] else ""')
    '"a  b" if [x] else ""'

`get_placeholders` returns the keys of the placeholders of a formula, each once
and in their order:

    >>> get_placeholders("[Ca] + [Ca.LDL] + [Mg] * [Ca]")
    ['Ca', 'Ca.LDL', 'Mg']

    >>> get_placeholders("1 + 2")
    []

`get_keyword` returns the keyword of a placeholder, without the suffix of a
value of a dependency:

    >>> get_keyword("Ca.LDL")
    'Ca'

    >>> get_keyword("Ca")
    'Ca'

`get_keywords` returns the keywords of the interim fields and services a
formula refers to:

    >>> get_keywords("[Ca] + [Ca.LDL] + [Mg]")
    ['Ca', 'Mg']


Globals of a formula
....................

A formula is evaluated without the builtins of Python, only with a set of
harmless functions and the `math` module:

    >>> globs = get_globals()
    >>> globs["__builtins__"] is None
    True

    >>> globs["math"]
    <module 'math' from '...'>

    >>> "__import__" in globs or "open" in globs or "eval" in globs
    False

The globals are a new mapping each time, so a change does not leak into the
next formula:

    >>> globs["min"] = None
    >>> get_globals()["min"]
    <built-in function min>

Keyword arguments are added to the globals:

    >>> get_globals(answer=42)["answer"]
    42

The Python imports of a calculation add a member of a module:

    >>> imports = [{"module": "math", "function": "floor"}]
    >>> get_globals(imports)["floor"]
    <built-in function floor>

`get_import` returns the member of one import, and an import that does not
exist is an error:

    >>> get_import({"module": "math", "function": "ceil"})
    <built-in function ceil>

    >>> get_globals([{"module": "math", "function": "nope"}])
    Traceback (most recent call last):
    ...
    ImportError: Could not find member nope of module math

`get_module_member` returns the member of a module, or `None`:

    >>> get_module_member("math", "ceil")
    <built-in function ceil>

    >>> get_module_member("math", "nope") is None
    True

    >>> get_module_member("no.such.module", "ceil") is None
    True

The names these helpers had before are still there:

    >>> getGlobals is get_globals and getModuleMember is get_module_member
    True


Binding values to a formula
...........................

`bind_values` replaces each placeholder by the name of a variable and returns
the expression together with its variables:

    >>> expression, variables = bind_values("[Ca] + [Mg]", {"Ca": 1.0, "Mg": 2.0})
    >>> expression
    'formula_value0 + formula_value1'

    >>> sorted(variables.items())
    [('formula_value0', 1.0), ('formula_value1', 2.0)]

A placeholder used twice is one variable:

    >>> expression, variables = bind_values("[Ca] * [Ca]", {"Ca": 3.0})
    >>> expression
    'formula_value0 * formula_value0'

Dotted placeholders refer to a value of a dependency, and the named
placeholders of the string formatting formulas were evaluated with before
still work:

    >>> expression, variables = bind_values(
    ...     "[Ca.LDL] + get_result(%(context_uid)s)",
    ...     {"Ca.LDL": 0.5, "context_uid": "abc"})
    >>> expression
    'formula_value1 + get_result(formula_value0)'

    >>> sorted(variables.items())
    [('formula_value0', 'abc'), ('formula_value1', 0.5)]

A placeholder without a value is an error:

    >>> bind_values("[Ca] + [Mg]", {"Ca": 1.0})
    Traceback (most recent call last):
    ...
    KeyError: 'Mg'


Evaluating a formula
....................

`evaluate_formula` binds the values and evaluates the formula:

    >>> evaluate_formula("[Ca] + [Mg]", {"Ca": 5.5, "Mg": 3.25})
    8.75

Numbers are used with their full precision:

    >>> evaluate_formula("[a] * 1", {"a": 1.23456789})
    1.23456789

String values are compared as strings:

    >>> formula = '"ok" if [var] == "example" else "no"'
    >>> evaluate_formula(formula, {"var": "example"})
    'ok'

    >>> evaluate_formula(formula, {"var": "other"})
    'no'

A value is never code, whatever text it holds:

    >>> formula = '"ok" if [var] == "example" else [var]'
    >>> evaluate_formula(formula, {"var": '"+str(1 + 1)+"'})
    '"+str(1 + 1)+"'

    >>> evaluate_formula(formula, {"var": "__import__('os').getcwd()"})
    "__import__('os').getcwd()"

The Python imports of the calculation are available to the formula:

    >>> imports = [{"module": "math", "function": "floor"}]
    >>> evaluate_formula("floor([Ca] + [Mg])", {"Ca": 5.6, "Mg": 3.3}, imports)
    8.0

A formula stored on several lines is evaluated on one:

    >>> evaluate_formula("[a]\n+\t[b]", {"a": 1, "b": 2})
    3

A formula that fails raises one of `FORMULA_ERRORS`:

    >>> for formula in ("[a] / 0", "[a] +", "nope([a])", "[a] + 'x'"):
    ...     try:
    ...         evaluate_formula(formula, {"a": 1})
    ...     except FORMULA_ERRORS as error:
    ...         print(type(error).__name__)
    ZeroDivisionError
    SyntaxError
    NameError
    TypeError


What a formula must not do
..........................

The globals of a formula hold no builtins of Python, but that alone does not
keep a formula in: through the internals of any object, e.g. `__class__` or
`__subclasses__`, a formula could reach the whole interpreter.
`check_formula` refuses a formula that uses an attribute starting with an
underscore or a name starting with two:

    >>> check_formula("[Ca] + [Mg]")

    >>> check_formula("().__class__.__bases__[0].__subclasses__()")
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use __subclasses__

    >>> check_formula("[Ca]._module")
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use _module

    >>> check_formula("__import__('os')")
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use __import__

Neither may a formula use the attributes that lead from an object to the
frames, the code or the globals of the interpreter, e.g. of a generator, a
frame or a function:

    >>> check_formula("[x for x in [1]].gi_frame")
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use gi_frame

    >>> check_formula("floor.f_back")
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use f_back

    >>> check_formula("floor.func_globals")
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use func_globals

    >>> check_formula("floor.im_func")
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use im_func

`evaluate_formula` compiles a formula with RestrictedPython, so every
attribute a formula reads at all goes through `get_formula_attribute`, which
refuses the same attributes, whatever way a formula gets to them:

    >>> get_formula_attribute(math, "func_globals")
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use func_globals

    >>> get_formula_attribute(math, "pi") == math.pi
    True

The `format` method of a text reads attributes itself, without any check,
so a formula must not use it:

    >>> evaluate_formula("'{}'.format([a])", {"a": 1})
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use format

Neither through the text type, which takes the text as its first argument:

    >>> evaluate_formula('str.format("{0.__class__}", [a])', {"a": 1})
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use format

Lambdas, comprehensions and the functions of a module keep working:

    >>> evaluate_formula("sum([v * 2 for v in [[a], [b]]])", {"a": 1, "b": 2})
    6

    >>> evaluate_formula("(lambda v: v + 1)([a])", {"a": 1})
    2

    >>> evaluate_formula("round(math.sqrt([a]), 2)", {"a": 2})
    1.41

A formula with placeholders, the older named placeholders, imports and the
attributes of a module stays allowed:

    >>> check_formula("floor([Ca] * math.pi) + get_result(%(context_uid)s)")

A formula that is not valid is a syntax error:

    >>> check_formula("[Ca] +")
    Traceback (most recent call last):
    ...
    SyntaxError: unexpected EOF while parsing

`evaluate_formula` checks every formula before it evaluates it, also one that
was stored before the check existed:

    >>> evaluate_formula("[a] if ().__class__ else 0", {"a": 1})
    Traceback (most recent call last):
    ...
    UnsafeFormula: A formula must not use __class__

`UnsafeFormula` is a `ValueError`, so it is one of `FORMULA_ERRORS` and an
analysis with such a formula gets no result instead of an error page:

    >>> issubclass(UnsafeFormula, FORMULA_ERRORS)
    True

    >>> calculate_formula("().__class__", {})
    'Unsafe formula: A formula must not use __class__'


Values of an analysis
.....................

`get_interim_value` returns the value of an interim field as a formula reads
it: a number, a text for an interim of a string type, or `None` when the
interim has no value:

    >>> get_interim_value({"keyword": "a", "value": "1.5"})
    1.5

    >>> get_interim_value({"keyword": "a", "value": "ok", "result_type": "string"})
    u'ok'

    >>> get_interim_value({"keyword": "a", "value": ""}) is None
    True

The value of a numeric interim must be a number:

    >>> get_interim_value({"keyword": "a", "value": "ok"})
    Traceback (most recent call last):
    ...
    ValueError: The value of a is not a number

`get_dependency_values` returns the result of a dependency and its limits, by
the keys a formula refers to them:

    >>> class Dependency(object):
    ...     def getKeyword(self): return "Ca"
    ...     def getLowerDetectionLimit(self): return "0.1"
    ...     def getUpperDetectionLimit(self): return "100"
    ...     def getLowerLimitOfQuantification(self): return "0.5"
    ...     def getUpperLimitOfQuantification(self): return "90"
    ...     def isBelowLowerDetectionLimit(self): return False
    ...     def isAboveUpperDetectionLimit(self): return False
    ...     def isBelowLimitOfQuantification(self): return True
    ...     def isAboveLimitOfQuantification(self): return False

    >>> values = get_dependency_values(Dependency(), 0.3)
    >>> for key in sorted(values):
    ...     print("{} {}".format(key, values[key]))
    Ca 0.3
    Ca.ABOVEUDL 0
    Ca.ABOVEULOQ 0
    Ca.BELOWLDL 0
    Ca.BELOWLLOQ 1
    Ca.BELOWLOQ 1
    Ca.LDL 0.1
    Ca.LLOQ 0.5
    Ca.LOQ 0.5
    Ca.RESULT 0.3
    Ca.UDL 100.0
    Ca.ULOQ 90.0

    >>> evaluate_formula("[Ca] * 2 if [Ca.BELOWLOQ] else [Ca]", values)
    0.6


Test parameters
...............

The test parameters of a calculation are entered as text. `to_test_value`
turns them into what the formula reads: numbers stay numbers, whole numbers
integers, anything else text without the quotes it may be written in:

    >>> to_test_value("5")
    5

    >>> to_test_value("5.5")
    5.5

    >>> to_test_value(10)
    10

    >>> to_test_value("'uncertain'")
    u'uncertain'

    >>> to_test_value("text")
    u'text'

`unquote` removes matching quotes only:

    >>> unquote('"quoted"')
    'quoted'

    >>> unquote("'mixed\"")
    '\'mixed"'

`calculate_formula` calculates the test result of a calculation:

    >>> formula = "[Comment] if [Comment] == 'uncertain' else [Ca] + [Mg]"
    >>> calculate_formula(formula, {"Ca": "5", "Mg": "5", "Comment": "'uncertain'"})
    u'uncertain'

    >>> calculate_formula(formula, {"Ca": "5", "Mg": "5", "Comment": "certain"})
    10

A test value is never code either:

    >>> formula = "[Comment] if [Comment] == 'x' else 'no'"
    >>> calculate_formula(formula, {"Comment": "x' or str(1 + 1) or 'x"})
    'no'

Errors are returned as text, for the test result field to show:

    >>> calculate_formula("[Ca] + [Mg]", {"Ca": "1"})
    'Key Error: Mg'

    >>> calculate_formula("[Ca] / [Mg]", {"Ca": "1", "Mg": "0"})
    'Division by 0: integer division or modulo by zero'

    >>> calculate_formula("[Ca] +", {"Ca": "1"})
    'Syntax Error: unexpected EOF while parsing'

    >>> calculate_formula("nope([Ca])", {"Ca": "1"})
    "Unspecified exception: name 'nope' is not defined"

    >>> calculate_formula("floor([Ca])", {"Ca": "1"},
    ...                   [{"module": "math", "function": "nope"}])
    'Import Error: Could not find member nope of module math'
