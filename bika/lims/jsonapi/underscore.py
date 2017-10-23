# -*- coding: utf-8 -*-

import ast
import json
import types


def fail(error):
    """ Raises a RuntimeError with the given error Message

        >>> fail("This failed badly")
        Traceback (most recent call last):
        ...
        RuntimeError: This failed badly
    """
    raise RuntimeError(error)


def is_string(thing):
    """ checks if an object is a string/unicode type

        >>> is_string("")
        True
        >>> is_string(u"")
        True
        >>> is_string(str())
        True
        >>> is_string(unicode())
        True
        >>> is_string(1)
        False
    """
    return type(thing) in types.StringTypes


def is_list(thing):
    """ checks if an object is a list type

        >>> is_list([])
        True
        >>> is_list(list())
        True
        >>> is_list("[]")
        False
        >>> is_list({})
        False
    """
    return isinstance(thing, types.ListType)


def is_tuple(thing):
    """ checks if an object is a tuple type

        >>> is_tuple(())
        True
        >>> is_tuple(tuple())
        True
        >>> is_tuple("()")
        False
        >>> is_tuple([])
        False
    """
    return isinstance(thing, types.TupleType)


def is_dict(thing):
    """ checks if an object is a dictionary type

        >>> is_dict({})
        True
        >>> is_dict(dict())
        True
        >>> is_dict("{}")
        False
        >>> is_dict([])
        False
    """
    return isinstance(thing, types.DictType)


def is_digit(thing):
    """ checks if an object is a digit

        >>> is_digit(1)
        True
        >>> is_digit("1")
        True
        >>> is_digit("a")
        False
        >>> is_digit([])
        False
    """
    return str(thing).isdigit()


def to_int(thing):
    """ coverts an object to int

        >>> to_int("0")
        0
        >>> to_int(1)
        1
        >>> to_int("1")
        1
        >>> to_int("a")

    """
    if is_digit(thing):
        return int(thing)
    return None


def to_string(thing):
    """ coverts an object to string

        >>> to_string(1)
        '1'
        >>> to_string([])
        '[]'
        >>> to_string(u"a")
        'a'
        >>> to_string(None)
        'None'
        >>> to_string(object())
        '<object ...>'
    """
    try:
        return str(thing)
    except UnicodeEncodeError:
        return thing.encode('ascii', 'replace')


def to_list(thing):
    """ converts an object to a list

        >>> to_list(1)
        [1]
        >>> to_list([1,2,3])
        [1, 2, 3]
        >>> to_list(("a", "b", "c"))
        ['a', 'b', 'c']
        >>> to_list(dict(a=1, b=2))
        [{'a': 1, 'b': 2}]
        >>> to_list(None)
        []
        >>> to_list("['a', 'b', 'c']")
        ['a', 'b', 'c']
        >>> to_list("")
        ['']
        >>> to_list([])
        []
        >>> to_list("['[]']")
        ['[]']
        >>> sorted(to_list(set(["a", "b", "c"])))
        ['a', 'b', 'c']
    """
    if thing is None:
        return []
    if isinstance(thing, set):
        return list(thing)
    if isinstance(thing, types.StringTypes):
        if thing.startswith("["):
            # handle a list inside a string coming from the batch navigation
            return ast.literal_eval(thing)
    if not (is_list(thing) or is_tuple(thing)):
        return [thing]
    return list(thing)


def convert(value, converter):
    """ Converts a value with a given converter function.

        >>> convert("1", to_int)
        1
        >>> convert("0", to_int)
        0
        >>> convert("a", to_int)

    """
    if not callable(converter):
        fail("Converter must be a function")
    return converter(value)


def pluck(col, key, default=None):
    """ Extracts a list of values from a collection of dictionaries

        >>> stooges = [{"name": "moe",   "age": 40},
        ...            {"name": "larry", "age": 50},
        ...            {"name": "curly", "age": 60}]
        >>> pluck(stooges, "name")
        ['moe', 'larry', 'curly']

        It only works with collections

        >>> curly = stooges.pop()
        >>> pluck(curly, "age")
        Traceback (most recent call last):
        ...
        RuntimeError: First argument must be a list or tuple
    """
    if not (is_list(col) or is_tuple(col)):
        fail("First argument must be a list or tuple")

    def _block(dct):
        if not is_dict(dct):
            return []
        return dct.get(key, default)

    return map(_block, col)


def pick(dct, *keys):
    """ Returns a copy of the dictionary filtered to only have values for the
        whitelisted keys (or list of valid keys)

        >>> pick({"name": "moe", "age": 50, "userid": "moe1"}, "name", "age")
        {'age': 50, 'name': 'moe'}

    """
    copy = dict()
    for key in keys:
        if key in dct.keys():
            copy[key] = dct[key]
    return copy


def omit(dct, *keys):
    """ Returns a copy of the dictionary filtered to omit the blacklisted keys
        (or list of keys)

        >>> omit({"name": "moe", "age": 50, "userid": "moe1"}, "userid", "age")
        {'name': 'moe'}
    """
    copy = dict()
    for key in dct:
        if key not in keys:
            copy[key] = dct[key]
    return copy


def rename(dct, mapping):
    """ Rename the keys of a dictionary with the given mapping

        >>> rename({"a": 1, "BBB": 2}, {"a": "AAA"})
        {'AAA': 1, 'BBB': 2}
    """

    def _block(memo, key):
        if key in dct:
            memo[mapping[key]] = dct[key]
            return memo
        else:
            return memo
    return reduce(_block, mapping, omit(dct, *mapping.keys()))


def alias(col, mapping):
    """ Returns a collection of dictionaries with the keys renamed according to
        the mapping

        >>> libraries = [{"isbn": 1, "ed": 1}, {"isbn": 2, "ed": 2}]
        >>> alias(libraries, {"ed": "edition"})
        [{'edition': 1, 'isbn': 1}, {'edition': 2, 'isbn': 2}]

        >>> alias({"a": 1}, {"a": "b"})
        [{'b': 1}]
    """
    if not is_list(col):
        col = [col]

    def _block(dct):
        return rename(dct, mapping)

    return map(_block, col)


def first(thing, n=0):
    """ get the first element of a list

        >>> lst = [1, 2, 3, 4, 5]
        >>> first(lst)
        1
        >>> first(lst, 3)
        [1, 2, 3]
        >>> first(lst, 10)
        [1, 2, 3, 4, 5]
        >>> first({"key": "value"})
        {'key': 'value'}
        >>> first(("a", "b", "c"))
        'a'
        >>> first([''])
        ''
        >>> first([''], 5)
        ['']
        >>> first(['', ''])
        ''
        >>> first(False)
        False
        >>> first("")
        ''
        >>> first(None)
        >>> first([])
    """
    n = to_int(n)
    if is_list(thing) or is_tuple(thing):
        if len(thing) == 0:
            return None
        if n > 0:
            return thing[0:n]
        return thing[0]
    return thing


def to_json(thing):
    """ parse to JSON

        >>> data = {}
        >>> to_json(data)
        '{}'
        >>> data = None
        >>> to_json(data)
        'null'
        >>> data = object()
        >>> to_json(data)
        ''
        >>> data = {"format": "json"}
        >>> to_json(data)
        '{"format": "json"}'
        >>> data = 1
        >>> to_json(data)
        '1'
    """
    try:
        return json.dumps(thing)
    except TypeError:
        return ""


if __name__ == '__main__':
    import doctest
    doctest.testmod(raise_on_error=False,
                    optionflags=doctest.ELLIPSIS |
                    doctest.NORMALIZE_WHITESPACE)
