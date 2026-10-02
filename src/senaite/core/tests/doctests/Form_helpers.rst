SENAITE form helpers
--------------------

The ``senaite.core.browser.form.helpers`` module normalizes form
payload reading for edit-form adapters. ZPublisher rewrites the input
``name`` attribute by appending a type marker (``:list``, ``:boolean``,
``:int`` …) so a field rendered as ``Hazardous`` arrives in the form
dict under one of several keys depending on the widget.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t Form_helpers


Test Setup
..........

    >>> from senaite.core.browser.form import helpers


``is_checked``: bool, list, string, None
........................................

Real booleans pass through unchanged:

    >>> helpers.is_checked(True)
    True

    >>> helpers.is_checked(False)
    False

DX boolean checkboxes submit a list containing one of the marker
values:

    >>> helpers.is_checked(["selected"])
    True

    >>> helpers.is_checked([])
    False

AT boolean fields submit a string. The accepted set is the narrow
list of tokens that boolean widgets actually emit; case and
surrounding whitespace are tolerated:

    >>> helpers.is_checked("true")
    True

    >>> helpers.is_checked("True")
    True

    >>> helpers.is_checked(" 1 ")
    True

    >>> helpers.is_checked("on")
    True

    >>> helpers.is_checked("selected")
    True

Anything else is treated as unchecked. An unexpected token never
silently means "checked":

    >>> helpers.is_checked("false")
    False

    >>> helpers.is_checked("0")
    False

    >>> helpers.is_checked("")
    False

    >>> helpers.is_checked("nope")
    False

    >>> helpers.is_checked(None)
    False


``get_form_value``: tolerant of ZPublisher type markers
.......................................................

A bare name lookup wins when present:

    >>> form = {"Hazardous": "yes"}
    >>> helpers.get_form_value(form, "Hazardous")
    'yes'

DX boolean checkboxes arrive suffixed with ``:list``:

    >>> form = {"Hazardous:list": ["selected"]}
    >>> helpers.get_form_value(form, "Hazardous")
    ['selected']

AT boolean fields arrive suffixed with ``:boolean``:

    >>> form = {"Hazardous:boolean": "1"}
    >>> helpers.get_form_value(form, "Hazardous")
    '1'

When several suffixed keys coexist, the lookup is deterministic
(sorted by key) so the result does not depend on dict ordering:

    >>> form = {
    ...     "Hazardous:list": ["selected"],
    ...     "Hazardous:boolean": "1",
    ... }
    >>> helpers.get_form_value(form, "Hazardous")
    '1'

Missing keys fall back to ``default``:

    >>> helpers.get_form_value({}, "Hazardous") is None
    True

    >>> helpers.get_form_value({}, "Hazardous", default="off")
    'off'

A bare name is not matched as a prefix of another field:

    >>> form = {"HazardousOther:boolean": "1"}
    >>> helpers.get_form_value(form, "Hazardous") is None
    True


``has_form_field``: presence regardless of suffix
.................................................

    >>> helpers.has_form_field({"Hazardous": "yes"}, "Hazardous")
    True

    >>> helpers.has_form_field({"Hazardous:list": []}, "Hazardous")
    True

    >>> helpers.has_form_field({}, "Hazardous")
    False

An empty value still counts as present — the field was submitted,
just empty:

    >>> helpers.has_form_field({"Hazardous:boolean": ""}, "Hazardous")
    True
