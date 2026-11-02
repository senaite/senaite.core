API Calculation
---------------

The calculation API evaluates the formulas of calculations. A formula refers
to the values it is calculated with by placeholders, e.g. `[Ca] + [Mg]`. The
values are bound to the formula as data and never become part of its text,
so a value cannot add code to the formula.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_calculation


Test Setup
..........

Needed Imports:

    >>> from senaite.core.api.calculation import *


Globals of a formula
....................

A formula is evaluated without the builtins of Python, only with a set of
harmless functions and the `math` module:

    >>> globs = getGlobals()
    >>> globs["__builtins__"] is None
    True

    >>> sorted(globs)[:6]
    ['__builtins__', 'all', 'any', 'bool', 'chr', 'cmp']

    >>> globs["math"]
    <module 'math' from '...'>

    >>> "__import__" in globs or "open" in globs or "eval" in globs
    False

Keyword arguments are added to the globals:

    >>> getGlobals(answer=42)["answer"]
    42

The Python imports of a calculation add a member of a module:

    >>> imports = [{"module": "math", "function": "floor"}]
    >>> getGlobals(imports)["floor"]
    <built-in function floor>

An import that does not exist is an error:

    >>> getGlobals([{"module": "math", "function": "nope"}])
    Traceback (most recent call last):
    ...
    ImportError: Could not find member nope of module math

`getModuleMember` returns the member of a module, or `None`:

    >>> getModuleMember("math", "ceil")
    <built-in function ceil>

    >>> getModuleMember("math", "nope") is None
    True

    >>> getModuleMember("no.such.module", "ceil") is None
    True


Binding values to a formula
...........................

`bind_values` replaces each placeholder by the name of a variable and returns
the expression together with its variables:

    >>> expression, variables = bind_values("[Ca] + [Mg]", {"Ca": 1.0, "Mg": 2.0})
    >>> expression
    '_value0 + _value1'

    >>> sorted(variables.items())
    [('_value0', 1.0), ('_value1', 2.0)]

A placeholder used twice is one variable:

    >>> expression, variables = bind_values("[Ca] * [Ca]", {"Ca": 3.0})
    >>> expression
    '_value0 * _value0'

Dotted placeholders refer to a value of a dependency, e.g. its detection
limit, and the named placeholders of the string formatting formulas were
evaluated with before still work:

    >>> expression, variables = bind_values(
    ...     "[Ca.LDL] + get_result(%(context_uid)s)",
    ...     {"Ca.LDL": 0.5, "context_uid": "abc"})
    >>> expression
    '_value1 + get_result(_value0)'

    >>> sorted(variables.items())
    [('_value0', 'abc'), ('_value1', 0.5)]

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

Line breaks and tabs in a stored formula mean nothing:

    >>> evaluate_formula("[a]\n+\t[b]\r", {"a": 1, "b": 2})
    3


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
