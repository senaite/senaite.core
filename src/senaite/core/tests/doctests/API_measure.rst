API Measure
-----------

The api_measure provides functions to operate with physical quantities and
units.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t API_measure

Test Setup
..........

Needed Imports

    >>> from senaite.core.api import measure as mapi


Get a magnitude object
......................

Magnitude-type objects are used to operate with physical quantities and
conversions while ensuring unit consistency:

    >>> mapi.get_magnitude("10.0mL")
    <magnitude.Magnitude instance at ...>

    >>> mapi.get_magnitude("15 ml")
    <magnitude.Magnitude instance at ...>

    >>> mapi.get_magnitude("0.23mg/L")
    <magnitude.Magnitude instance at ...>

If no valid units are provided, an error arises:

    >>> mapi.get_magnitude("0.23po")
    Traceback (most recent call last):
    [...]
    APIError: Don't know about unit po

An error arises too when the value is not from a valid type:

    >>> mapi.get_magnitude(None)
    Traceback (most recent call last):
    [...]
    APIError: None is not supported.

    >>> mapi.get_magnitude((10, "ml"))
    Traceback (most recent call last):
    [...]
    APIError: (10, 'ml') is not supported.

An error arises if the value type is valid but with wrong format:

    >>> mapi.get_magnitude("1")
    Traceback (most recent call last):
    [...]
    APIError: No valid format: 1

    >>> mapi.get_magnitude("ml")
    Traceback (most recent call last):
    [...]
    APIError: No valid format: ml

    >>> mapi.get_magnitude("10ml 12ml")
    Traceback (most recent call last):
    [...]
    APIError: Don't know about unit 12ml

    >>> mapi.get_magnitude("10 20.34 ml")
    Traceback (most recent call last):
    [...]
    APIError: Don't know about unit 20.3

We can also pass another magnitude as the value:

    >>> mg = mapi.get_magnitude("10ml")
    >>> mapi.get_magnitude(mg)
    <magnitude.Magnitude instance at ...>

We can make use of the default param for fallback return:

    >>> mapi.get_magnitude(None, default="10ml")
    <magnitude.Magnitude instance at ...>

    >>> mg = mapi.get_magnitude("10.0ml")
    >>> mapi.get_magnitude(None, default=mg)
    <magnitude.Magnitude instance at ...>

But default must be convertible too:

    >>> mapi.get_magnitude(None, default=None)
    Traceback (most recent call last):
    [...]
    APIError: None is not supported.

    >>> mapi.get_magnitude(None, default="1")
    Traceback (most recent call last):
    [...]
    APIError: No valid format: 1


Check if the value is from magnitude type
.........................................

We can check if a given value is an instance of a magnitude type as follows:

    >>> mapi.is_magnitude(None)
    False

    >>> mapi.is_magnitude(object())
    False

    >>> mapi.is_magnitude("10ml")
    False

    >>> mg = mapi.get_magnitude("10ml")
    >>> mapi.is_magnitude(mg)
    True


Get the float quantity
......................

We can easily get the quantity part of the value as a float:

    >>> mapi.get_quantity("10ml")
    10.0

    >>> mapi.get_quantity("10.4g")
    10.4

We can even pass a Magnitude object:

    >>> mg = mapi.get_magnitude("10.5 mL")
    >>> mapi.get_quantity(mg)
    10.5

But an error arises if the value is not suitable:

    >>> mapi.get_quantity(None)
    Traceback (most recent call last):
    [...]
    APIError: None is not supported.

    >>> mapi.get_quantity("1")
    Traceback (most recent call last):
    [...]
    APIError: No valid format: 1

    >>> mapi.get_quantity("0.23po")
    Traceback (most recent call last):
    [...]
    APIError: Don't know about unit po


Conversion of a quantity to another unit
........................................

We can easily convert a quantity to another unit:

    >>> mapi.get_quantity("1mL", unit="L")
    0.001

    >>> mapi.get_quantity("1mL", unit="dL")
    0.01

    >>> mapi.get_quantity("10.2L", unit="mL")
    10200.0


Check volumes
.............

The api makes the check of volumes easy:

    >>> mapi.is_volume("10mL")
    True

    >>> mapi.is_volume("2.3 L")
    True

    >>> mapi.is_volume("0.02 dl")
    True

    >>> mapi.is_volume("10mg")
    False

    >>> mapi.is_volume("2.3 kg")
    False

    >>> mapi.is_volume("0.02 dg")
    False

    >>> mapi.is_volume(2)
    False

    >>> mapi.is_volume(None)
    False


Check weights
.............

The api makes the check of volumes easy:

    >>> mapi.is_weight("10mg")
    True

    >>> mapi.is_weight("2.3 kg")
    True

    >>> mapi.is_weight("0.02 dg")
    True

    >>> mapi.is_weight("10mL")
    False

    >>> mapi.is_weight("2.3 L")
    False

    >>> mapi.is_weight("0.02 dl")
    False

    >>> mapi.is_weight(2)
    False

    >>> mapi.is_weight(None)
    False
