Alphanumber
===========

Tests the Alphanumber object, useful for alphanumeric IDs generation

Running this test from the buildout directory::

    bin/test test_textual_doctests -t Alphanumber


Test Setup
----------

Needed Imports:

    >>> import re
    >>> from bika.lims import api
    >>> from bika.lims.alphanumber import to_decimal
    >>> from bika.lims.alphanumber import Alphanumber

Create and test basic alphanumeric functions:

    >>> alpha = Alphanumber(0)
    >>> int(alpha)
    0
    >>> str(alpha)
    'AAA000'
    >>> repr(alpha)
    'AAA000'
    >>> format(alpha, "2a2d")
    'AA00'
    >>> alpha.format("5a4d")
    'AAAAA0000'
    >>> "{alpha:2a4d}".format(alpha=alpha)
    'AA0000'
    >>> alpha1 = alpha + 1
    >>> int(alpha1)
    1
    >>> str(alpha1)
    'AAA001'
    >>> repr(alpha1)
    'AAA001'
    >>> format(alpha1, "2a2d")
    'AA01'
    >>> alpha1.format("5a4d")
    'AAAAA0001'
    >>> "{alpha:2a4d}".format(alpha=alpha1)
    'AA0001'
    >>> alpha2 = Alphanumber(2674, num_digits=2)
    >>> int(alpha2)
    2674
    >>> str(alpha2)
    'ABB01'

Addition of an integer:

    >>> alpha3 = alpha2 + 1
    >>> int(alpha3)
    2675
    >>> str(alpha3)
    'ABB02'
    >>> to_decimal(str(alpha3))
    2675

Addition of another Alphanumber object:

    >>> alpha3 = alpha2 + alpha1
    >>> int(alpha3)
    2675
    >>> str(alpha3)
    'ABB02'
    >>> alpha3 = alpha2 + alpha2
    >>> int(alpha3)
    5348
    >>> str(alpha3)
    'ACC02'
    >>> to_decimal(str(alpha3))
    5348

Subtraction of an integer:

    >>> alpha3 = alpha2 - 1
    >>> int(alpha3)
    2673
    >>> str(alpha3)
    'ABA99'
    >>> to_decimal(str(alpha3))
    2673

Subtraction of another Alphanumber object:

    >>> alpha3 = alpha2 - alpha1
    >>> int(alpha3)
    2673
    >>> str(alpha3)
    'ABA99'
    >>> alpha3 = alpha2 - alpha2
    >>> int(alpha3)
    0
    >>> str(alpha3)
    'AAA00'
    >>> to_decimal(str(alpha3))
    0

We can also create the instance with a string representing an alpha number:

    >>> alpha = Alphanumber("ABB23", num_chars=3, num_digits=2)
    >>> str(alpha)
    'ABB23'
    >>> int(alpha)
    2696
    >>> to_decimal(str(alpha))
    2696

We can even change the number of digits to default (3 digits) and the result
will be formatted accordingly:

    >>> alpha = Alphanumber("ABB23")
    >>> str(alpha)
    'AAC698'
    >>> int(alpha)
    2696

Or we can do the same, but using another Alphanumber instance as argument:

    >>> alpha = Alphanumber(alpha, num_chars=2)
    >>> str(alpha)
    'AC698'
    >>> int(alpha)
    2696

We can also use our own alphabet:

    >>> alpha = Alphanumber(alpha, alphabet="yu")
    >>> str(alpha)
    'yuy698'
    >>> int(alpha)
    2696
    >>> to_decimal(str(alpha), alphabet="yu")
    2696

And we can add or subtract regardless of alphabet, number of digits and number
of characters:

    >>> alpha1 = Alphanumber("ABB23")
    >>> int(alpha1)
    2696
    >>> alpha2 = Alphanumber("yu753", alphabet="yu")
    >>> int(alpha2)
    1752
    >>> alpha3 = alpha1 + alpha2
    >>> int(alpha3)
    4448
    >>> str(alpha3)
    'AAE452'

Formatted value must change when a different number of digits is used:

    >>> str(alpha3)
    'AAE452'
    >>> format(alpha3, "2a3d")
    'AE452'
    >>> format(alpha3, "5a3d")
    'AAAAE452'
    >>> format(alpha3, "3a2d")
    'ABS92'

We can also compare two Alphanumbers:

    >>> alpha3 > alpha2
    True

    >>> alpha1 > alpha3
    False

    >>> alpha4 = Alphanumber(4448)
    >>> alpha3 == alpha4
    True

Or get the max and the min:

    >>> alphas = [alpha1, alpha3, alpha2]
    >>> alpha_max = max(alphas)
    >>> int(alpha_max)
    4448

    >>> alpha_min = min(alphas)
    >>> int(alpha_min)
    1752

We can also convert to int directly:

    >>> int(alpha4)
    4448

Or use the lims api:

    >>> api.to_int(alpha4)
    4448
