# -*- coding: utf-8 -*-

# Python 3 compatibility module


def cmp(a, b):
    """Polyfill for the `cmp` builtin function

    https://docs.python.org/3.0/whatsnew/3.0.html#ordering-comparisons

    The cmp() function should be treated as gone, and the __cmp__() special
    method is no longer supported. Use __lt__() for sorting, __eq__() with
    __hash__(), and other rich comparisons as needed. (If you really need the
    cmp() functionality, you could use the expression (a > b) - (a < b) as the
    equivalent for cmp(a, b).)
    """
    return (a > b) - (a < b)
