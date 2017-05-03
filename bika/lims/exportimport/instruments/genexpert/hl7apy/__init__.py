# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2015, CRS4
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import
import os
import sys
import collections
import importlib
try:
    import cPickle as pickle
except ImportError:
    import pickle

from bika.lims.exportimport.instruments.genexpert.hl7apy.exceptions import UnsupportedVersion, InvalidEncodingChars, UnknownValidationLevel
from bika.lims.exportimport.instruments.genexpert.hl7apy.consts import DEFAULT_ENCODING_CHARS, DEFAULT_VERSION, VALIDATION_LEVEL

__author__ = 'Daniela Ghironi, Vittorio Meloni, Alessandro Sulis, Federico Caboni'
__author_email__ = '<ghiron@gmail.com>, <vittorio.meloni@crs4.it>, <alessandro.sulis@crs4.it>, ' \
                   '<federico.caboni@me.com>'
__url__ = 'http://hl7apy.org'

_DEFAULT_ENCODING_CHARS = DEFAULT_ENCODING_CHARS
_DEFAULT_VERSION = DEFAULT_VERSION
_DEFAULT_VALIDATION_LEVEL = VALIDATION_LEVEL.TOLERANT


def check_encoding_chars(encoding_chars):
    """
    Validate the given encoding chars

    :type encoding_chars: ``dict``
    :param encoding_chars: the encoding chars (see :func:`hl7apy.set_default_encoding_chars`)
    :raises: :exc:`hl7apy.exceptions.InvalidEncodingChars` if the given encoding chars are not valid
    """
    if not isinstance(encoding_chars, collections.MutableMapping):
        raise InvalidEncodingChars
    required = {'FIELD', 'COMPONENT', 'SUBCOMPONENT', 'REPETITION', 'ESCAPE'}
    missing = required - set(encoding_chars.keys())
    if missing:
        raise InvalidEncodingChars('Missing required encoding chars')

    values = [v for k, v in encoding_chars.items() if k in required]
    if len(values) > len(set(values)):
        raise InvalidEncodingChars('Found duplicate encoding chars')


def check_validation_level(validation_level):
    """
    Validate the given validation level

    :type validation_level: ``int``
    :param validation_level: validation level (see :class:`hl7apy.consts.VALIDATION_LEVEL`)
    :raises: :exc:`hl7apy.exceptions.UnknownValidationLevel` if the given validation level is unsupported
    """
    if validation_level not in (VALIDATION_LEVEL.QUIET, VALIDATION_LEVEL.STRICT, VALIDATION_LEVEL.TOLERANT):
        raise UnknownValidationLevel


def check_version(version):
    """
    Validate the given version number

    :type version: ``str``
    :param version: the version to validate (e.g. ``2.6``)
    :raises: :class:`hl7apy.exceptions.UnsupportedVersion` if the given version is unsupported
    """
    if version not in SUPPORTED_LIBRARIES:
        raise UnsupportedVersion(version)


def get_default_encoding_chars():
    """
    Get the default encoding chars

    :rtype: ``dict``
    :returns: the encoding chars (see :func:`hl7apy.set_default_encoding_chars`)

    >>> print(get_default_encoding_chars()['FIELD'])
    |
    """
    return _DEFAULT_ENCODING_CHARS


def get_default_version():
    """
    Get the default version

    :rtype: ``str``
    :returns: the default version

    >>> print(get_default_version())
    2.5
    """
    return _DEFAULT_VERSION


def get_default_validation_level():
    """
    Get the default validation level

    :rtype: ``str``
    :returns: the default validation level

    >>> print(get_default_validation_level())
    2
    """
    return _DEFAULT_VALIDATION_LEVEL


def set_default_validation_level(validation_level):
    """
    Set the given validation level as default

    :type validation_level: ``int``
    :param validation_level: validation level (see :class:`hl7apy.consts.VALIDATION_LEVEL`)
    :raises: :exc:`hl7apy.exceptions.UnknownValidationLevel` if the given validation level is unsupported

    >>> set_default_validation_level(3)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    UnknownValidationLevel
    >>> set_default_validation_level(VALIDATION_LEVEL.TOLERANT)
    >>> print(get_default_validation_level())
    2
    """
    check_validation_level(validation_level)

    global _DEFAULT_VALIDATION_LEVEL

    _DEFAULT_VALIDATION_LEVEL = validation_level


def set_default_version(version):
    """
    Set the given version as default

    :type version: ``str``
    :param version: the new default version (e.g. ``2.6``)
    :raises: :class:`hl7apy.exceptions.UnsupportedVersion` if the given version is unsupported

    >>> set_default_version('22')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    UnsupportedVersion: The version 22 is not supported
    >>> set_default_version('2.3')
    >>> print(get_default_version())
    2.3
    """
    check_version(version)

    global _DEFAULT_VERSION

    _DEFAULT_VERSION = version


def set_default_encoding_chars(encoding_chars):
    """
    Set the given encoding chars as default

    :type encoding_chars: ``dict``
    :param encoding_chars: the new encoding chars
    :raises: :class:`hl7apy.exceptions.InvalidEncodingChars` if the given encoding chars are not valid

    The *encoding_chars* dictionary should contain the following keys:

    +--------------+-----------------+
    |Key           |Default          |
    +==============+=================+
    |GROUP         |``\\r``           |
    +--------------+-----------------+
    |SEGMENT       |``\\r``           |
    +--------------+-----------------+
    |FIELD         |``|``            |
    +--------------+-----------------+
    |COMPONENT     |``^``            |
    +--------------+-----------------+
    |SUBCOMPONENT  |``&``            |
    +--------------+-----------------+
    |REPETITION    |``~``            |
    +--------------+-----------------+
    |ESCAPE        |``\\``            |
    +--------------+-----------------+

    >>> set_default_encoding_chars({'FIELD': '!'})  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    InvalidEncodingChars: Missing required encoding chars
    >>> set_default_encoding_chars({'FIELD': '!', 'COMPONENT': 'C', 'SUBCOMPONENT': 'S', \
                                    'REPETITION': 'R', 'ESCAPE': '\\\\'})
    >>> print(get_default_encoding_chars()['FIELD'])
    !
    """
    check_encoding_chars(encoding_chars)

    encoding_chars.update({'GROUP': '\r', 'SEGMENT': '\r'})

    global _DEFAULT_ENCODING_CHARS

    _DEFAULT_ENCODING_CHARS = encoding_chars


def load_library(version):
    """
    Load the correct module according to the version

    :type version: ``str``
    :param version: the version of the library to be loaded (e.g. '2.6')
    :rtype: module object
    """
    check_version(version)
    module_name = SUPPORTED_LIBRARIES[version]
    lib = sys.modules.get(module_name)
    if lib is None:
        lib = importlib.import_module(module_name)
    return lib


def load_reference(name, element_type, version):
    """
    Look for an element of the given type, name and version and return its reference structure

    :type element_type: ``str``
    :param element_type: the element type to look for (e.g. 'Segment')
    :type name: ``str``
    :param name: the element name to look for (e.g. 'MSH')
    :type version: ``str``
    :param version: the version of the library where to search the element (e.g. '2.6')
    :rtype: ``dict``
    :return: a dictionary describing the element structure
    :raise: ``KeyError`` if the element has not been found

    The returned dictionary will contain the following keys:

    +--------------+--------------------------------------------+
    |Key           |Value                                       |
    +==============+============================================+
    |cls           |an :class:`hl7apy.core.Element` subclass    |
    +--------------+--------------------------------------------+
    |name          |the Element name (e.g. PID)                 |
    +--------------+--------------------------------------------+
    |ref           |a tuple of one of the following format:     |
    |              |                                            |
    |              |('leaf', <datatype>, <longName>, <table>)   |
    |              |('sequence', (<child>, (<min>, <max>), ...))|
    +--------------+--------------------------------------------+

    >>> load_reference('UNKNOWN', 'Segment', '2.5')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ChildNotFound: No child named UNKNOWN
    >>> r = load_reference('ADT_A01', 'Message', '2.5')
    >>> print(r[0])
    sequence
    >>> r = load_reference('MSH_3', 'Field', '2.5')
    >>> print(r[0])
    leaf
    """
    lib = load_library(version)
    ref = lib.get(name, element_type)
    return ref


def find_reference(name, element_types, version):
    """
    Look for an element of the given name and version into the given types and return its reference structure

    :type name: ``str``
    :param name: the element name to look for (e.g. 'MSH')
    :type types: ``list`` or ``tuple``
    :param types: the element classes where to look for the element (e.g. (Group, Segment))
    :type version: ``str``
    :param version: the version of the library where to search the element (e.g. '2.6')
    :rtype: ``dict``
    :return: a dictionary describing the element structure
    :raise: :class:`hl7apy.exceptions.ChildNotFound` if the element has not been found

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.core import Message, Segment
    >>> find_reference('UNKNOWN', (Segment, ), '2.5')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ChildNotFound: No child named UNKNOWN
    >>> find_reference('ADT_A01', (Segment,),  '2.5')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ChildNotFound: No child named ADT_A01
    >>> r = find_reference('ADT_A01', (Message,),  '2.5')
    >>> print('%s %s' % (r['name'], r['cls']))
    ADT_A01 <class 'hl7apy.core.Message'>
    """
    lib = load_library(version)
    ref = lib.find(name, element_types)
    return ref


def load_message_profile(path):
    with open(path, 'rb') as f:
        mp = pickle.load(f)

    return mp


def _discover_libraries():
    current_dir = os.path.dirname(__file__)
    return {o[1:].replace("_", "."): "hl7apy.{}".format(o)
            for o in os.listdir(current_dir) if o.startswith("v2_")}

SUPPORTED_LIBRARIES = _discover_libraries()

if __name__ == '__main__':

    import doctest
    doctest.testmod()
