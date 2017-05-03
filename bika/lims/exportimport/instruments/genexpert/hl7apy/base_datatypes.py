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
"""
.. warning::

    The HL7 versions can have different implementation of base datatypes; for example the ST base datatype
    of HL7 v2.6 is different from the v2.5 one. This module contains reference classes for all base datatypes
    but you should not import them directly from here. If you need an implementation for a particular version
    use the :func:`get_base_datatypes` function from a specific version's module
    For example if you're using version 2.4 and you need an `FT` base datatype do the following:

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.v2_4 import FT
    >>> f = FT('some useful information')

"""

from __future__ import absolute_import
import re
import numbers
from datetime import datetime
from decimal import Decimal
from functools import cmp_to_key

from bika.lims.exportimport.instruments.genexpert.hl7apy import get_default_encoding_chars, get_default_validation_level
from bika.lims.exportimport.instruments.genexpert.hl7apy.exceptions import MaxLengthReached, InvalidHighlightRange, InvalidDateFormat, \
    InvalidDateOffset, InvalidMicrosecondsPrecision
from bika.lims.exportimport.instruments.genexpert.hl7apy.validation import Validator


class BaseDataType(object):
    """
    Generic datatype base class. It handles the value of the data type and its
    maximum length. It is meant to be extended and it should not be used directly

    :param value: the value of the data type

    :type max_length: ``int``
    :param max_length: The maximum length of the value. Default to None

    :type validation_level: ``int``
    :param validation_level: It must be a value from class
        :class:`VALIDATION_LEVEL <hl7apy.consts.VALIDATION_LEVEL>`
        If it is :attr:`STRICT <VALIDATION_LEVEL.STRICT>` it checks that :attr:`value` doesn't exceed the
        attr:`max_length`

    :raise: :exc:`MaxLengthReached <hl7apy.exceptions.MaxLengthReached>` When the :attr:`value`'s length is
        greater than the :attr:`max_length`. Only if :attr:`validation_level` is
        :attr:`STRICT <VALIDATION_LEVEL.STRICT>`
    """
    def __init__(self, value, max_length=None, validation_level=None):
        if validation_level is None:
            validation_level = get_default_validation_level()
        self.validation_level = validation_level
        self.max_length = max_length
        if Validator.is_strict(self.validation_level):
            if self.max_length is not None and len('{0}'.format(value)) > self.max_length:
                raise MaxLengthReached(value, self.max_length)
        self.value = value

    def to_er7(self, encoding_chars=None):
        """
        Encode to ER7 format
        """
        return '{0}'.format(self.value if self.value is not None else '')

    @property
    def classname(self):
        """
        The name of the class
        """
        return self.__class__.__name__


class TextualDataType(BaseDataType):
    """
    Base class for textual data types.
    It is meant to be extended and it should not be used directly

    :type value: ``str``
    :param value: the value of the data type

    :type max_length: ``int``
    :param max_length: the max length of the value (default to 32)

    :type highlights: ``tuple``, ``list``
    :param highlights: a list of ranges indicating the part
        of the value to be highlighted. e.g. ((0,5), (6,7))
        The highlights cannot overlap, if they do an HL7Exception will be
        thrown when to_er7 method is called

    :type validation_level: ``int``
    :param validation_level: It has the same meaning as in
        :class:`BaseDatatype <hl7apy.base_datatype.BaseDatatype>`

    :raise: :exc:`MaxLengthReached <hl7apy.exceptions.MaxLengthReached>` When the :attr:`value`'s length is
        greater than :attr:`max_length`
    """
    def __init__(self, value, max_length=32, highlights=None,
                 validation_level=None):
        self.highlights = highlights
        super(TextualDataType, self).__init__(value, max_length,
                                              validation_level)

    def to_er7(self, encoding_chars=None):
        if encoding_chars is None:
            encoding_chars = get_default_encoding_chars()
        return self._escape_value(self.value, encoding_chars)

    def _escape_value(self, value, encoding_chars=None):
        escape_char = encoding_chars['ESCAPE']
        translations = ((encoding_chars['FIELD'], '{esc}F{esc}'.format(esc=escape_char)),
                        (encoding_chars['COMPONENT'], '{esc}S{esc}'.format(esc=escape_char)),
                        (encoding_chars['SUBCOMPONENT'], '{esc}T{esc}'.format(esc=escape_char)),
                        (encoding_chars['REPETITION'], '{esc}R{esc}'.format(esc=escape_char)))

        # Inserts the highlights escape sequences
        if self.highlights is not None:
            def _sort_highlights(x, y):
                if x[0] < y[0]:
                    if y[0] < x[1]:  # overlapping ranges
                        raise InvalidHighlightRange(x, y)
                    else:
                        return -1
                elif x[0] > y[0]:
                    if x[0] < y[1]:  # overlapping ranges
                        raise InvalidHighlightRange(x, y)
                    else:
                        return 1
                else:
                    raise InvalidHighlightRange(x, y)

            self.highlights = sorted(self.highlights, key=cmp_to_key(_sort_highlights))
            words = list(value)
            offset = 0
            for hl in self.highlights:
                if hl[0] > hl[1]:
                    raise InvalidHighlightRange(hl[0], hl[1])
                words.insert(hl[0] + offset, '{esc}H{esc}'.format(esc=escape_char))
                words.insert(hl[1] + offset + 1, '{esc}N{esc}'.format(esc=escape_char))
                offset += 2
            value = ''.join(words)

        # Escapes encoding_chars
        for char, esc_seq in translations:
            value = value.replace(char, esc_seq)
        # Escapes the escape_char. If it is found in other escape sequences it is not escaped.
        # For example if the escape char is / and we find /H/ the escape chars are not re-escaped,
        # otherwise it would become /E/H/E/ which is not the result wanted.
        # Thus the regex search for escape chars not followed and not preceeded by one of the litteral
        # composing an escape sequence. We use lambda because otherwise the backslash sequence in the string
        # is processed (look for re.sub in python doc) and we don't want this
        value = re.sub('(?<!%s[HNFSTRE])%s(?![HNFSTRE]%s)' % tuple(3*[re.escape(escape_char)]),
                       lambda x: '{esc}E{esc}'.format(esc=escape_char), value)

        return value


class NumericDataType(BaseDataType):
    """
    Base class for numeric data types.
    It is meant to be extended and it should not be used directly

    :param value: the value of the data type. Default is ``None``

    :type max_length: int
    :param max_length: The maximum number of digit in the value. Default is 16

    :type validation_level: ``int``
    :param validation_level: It has the same meaning as in :class:`hl7apy.base_datatypes.BaseDataType`

    :raise: :exc:`hl7apy.exceptions.MaxLengthReached` When the `value`'s length is greater than `max_length`

    """
    def __init__(self, value=None, max_length=16,
                 validation_level=None):
        super(NumericDataType, self).__init__(value, max_length,
                                              validation_level)


class DateTimeDataType(BaseDataType):
    """
    Base class for datetime data types.
    It is meant to be extended and it should not be used directly.
    Children classes should at least override the :attr:`allowed_formats` tuple

    :type value datetime: datetime.datetime
    :param value: a `datetime` date object. Default is ``None``

    :type out_format: str
    :param out_format: the format that will be used converting the object to string.
        It must be an item of the :attr:`allowed_formats` tuple

    :raise: :exc:``InvalidDateFormat <hl7apy.exceptions.InvalidDateFormat>` if the ``format`` is not in
        the :attr:`allowed_formats` member
    """

    allowed_formats = ()

    def __init__(self, value=None, out_format=''):
        if out_format not in self.allowed_formats:
            raise InvalidDateFormat(out_format)
        self.value = value
        self.format = out_format

    def to_er7(self, encoding_chars=None):
        return datetime.strftime(self.value, self.format)


class DT(DateTimeDataType):
    """
    Class for DT base datatype. It extends DatetimeDatatype and it represents a time value with
    year, month and day. Parameters are the same of the superclass.

    The :attr:`allowed_formats` tuple is ``('%Y', '%Y%m', '%Y%m%d')``
    """

    allowed_formats = ('%Y', '%Y%m', '%Y%m%d')

    def __init__(self, value=None, out_format='%Y%m%d'):
        super(DT, self).__init__(value, out_format)


class TM(DateTimeDataType):
    """
    Class for TM base datatype. It extends DateTimeDatatype and it represents a time value with
    hours, minutes, seconds and microseconds. Parameters are the same of the superclass plus ``offset``.
    Since HL7 supports only four digits for microseconds, and Python datetime uses 6 digits, the wanted
    precision must be specified.

    The :attr:`allowed_formats` tuple is ``('%H', '%H%M', '%H%M%S', '%H%M%S.%f')``.
    It needs also the ``offset`` parameter which represents the UTC offset

    :type offset: ``str``
    :param offset: the UTC offset. By default it is ''. It must be in the form ``'+/-HHMM'``

    :type microsec_precision: ``int``
    :param microsec_precision: Number of digit of the microseconds part of the value.
        It must be between 1 and 4
    """

    allowed_formats = ('%H', '%H%M', '%H%M%S', '%H%M%S.%f')

    def __init__(self, value=None, out_format='%H%M%S.%f', offset='', microsec_precision=4):
        super(TM, self).__init__(value, out_format)

        if not (1 <= microsec_precision <= 4):
            raise InvalidMicrosecondsPrecision()

        self.microsec_precision = microsec_precision

        if offset and len(offset) != 5:
            raise InvalidDateOffset(offset)
        try:
            d = datetime.strptime(offset[1:], '%H%M')
            if d.hour > 12:
                raise ValueError
        except ValueError:
            if offset:
                raise InvalidDateOffset(offset)

        if offset and offset[0] not in ('+', '-'):
            raise InvalidDateOffset(offset)

        self.offset = offset

    def to_er7(self, encoding_chars=None):
        date_value = super(TM, self).to_er7()
        if self.format.find('%f') != -1:
            index = 6 - self.microsec_precision
            date_value = date_value[:-index]
        return '{0}{1}'.format(date_value, self.offset)


class DTM(TM):
    """
    Class for DTM base datatype. It extends TM and it represents classes DT and DTM combined.
    Thus it represents year, month, day, hours, minutes, seconds and microseconds.
    Parameters are the same of the superclass.

    The :attr:`allowed_formats` tuple is
    ``('%Y', '%Y%m', '%Y%m%d', '%Y%m%d%H', '%Y%m%d%H%M', '%Y%m%d%H%M%S', '%Y%m%d%H%M%S.%f')``
    """

    allowed_formats = ('%Y', '%Y%m', '%Y%m%d', '%Y%m%d%H', '%Y%m%d%H%M',
                       '%Y%m%d%H%M%S', '%Y%m%d%H%M%S.%f')

    def __init__(self, value=None, out_format='%Y%m%d%H%M%S.%f', offset='', microsec_precision=4):
        super(DTM, self).__init__(value, out_format, offset, microsec_precision)


class ST(TextualDataType):
    """
    Class for ST datatype. It extends :class:`hl7apy.base_datatypes.TextualDatatype` and the parameters are
    the same of the superclass

    :attr:`max_length` is 199
    """
    def __init__(self, value, highlights=None,
                 validation_level=None):
        super(ST, self).__init__(value, 199, highlights, validation_level)


class FT(TextualDataType):
    """
    Class for FT datatype. It extends :class:`hl7apy.base_datatypes.TextualDataType` and the parameters are
    the same of the superclass

    :attr:`max_length` is 65536
    """
    def __init__(self, value, highlights=None,
                 validation_level=None):
        super(FT, self).__init__(value, 65536, highlights, validation_level)


class ID(TextualDataType):
    """
    Class for ID datatype. It extends :class:`hl7apy.base_datatypes.TextualDataType` and the parameters are
    the same of the superclass

    :attr:`max_length` None
    """
    def __init__(self, value, highlights=None,
                 validation_level=None):
        # max_length is None bacause it depends from the HL7 table
        super(ID, self).__init__(value, None, highlights, validation_level)
        # TODO: check for tables of allowed values: are we strict or not?


class IS(TextualDataType):
    """
    Class for IS datatype. It extends :class:`hl7apy.base_datatypes.TextualDataType` and the parameters are
    the same of the superclass

    :attr:`max_length` is 20
    """
    def __init__(self, value, highlights=None,
                 validation_level=None):
        super(IS, self).__init__(value, 20, highlights, validation_level)
        # TODO: check for tables of allowed values (also defined on site): are we strict or not?


class TX(TextualDataType):
    """
    Class for TX datatype. It extends :class:`hl7apy.base_datatypes.TextualDataType` and the parameters are
    the same of the superclass

    :attr:`max_length` is 65536
    """
    def __init__(self, value, highlights=None,
                 validation_level=None):
        super(TX, self).__init__(value, 65536, highlights, validation_level)


class GTS(TextualDataType):
    """
    Class for GTS datatype. It extends :class:`hl7apy.base_datatypes.TextualDataType` and the parameters are
    the same of the superclass

    :attr:`max_length` is 199
    """
    def __init__(self, value, highlights=None,
                 validation_level=None):
        super(GTS, self).__init__(value, 199, highlights, validation_level)


class NM(NumericDataType):
    """
    Class for NM datatype. It extends :class:`hl7apy.base_datatypes.NumericDatatype` and the parameters are
    the same of the superclass

    :attr:`max_length` is 16.

    The type of ``value`` must be :class:`decimal.Decimal` or :class:`Real <numbers.Real>`

    :raise: :exc:`ValueError` raised when the value is not of one of the correct type
    """

    def __init__(self, value=None,
                 validation_level=None):
        if value is not None and isinstance(value, numbers.Real):
            value = Decimal(value)
        elif value is not None and not isinstance(value, Decimal):
            raise ValueError('Invalid value for a NM data')
        super(NM, self).__init__(value, 16, validation_level)


class SI(NumericDataType):
    """
    Class for NM datatype. It extends NumericDatatype and the parameters are the same of the superclass

    :attr:`max_length` is 4.

    The type of ``value`` must be `int` or :class:`numbers.Integral`

    :raise: :exc:`ValueError` raised when the value is not of one of the correct type
    """
    def __init__(self, value=None,
                 validation_level=None):
        if value is not None and not isinstance(value, numbers.Integral):
            raise ValueError('Invalid value for a SI data')

        super(SI, self).__init__(value, 4, validation_level)


class TN(TextualDataType):
    """
    Class for TN datatype. It extends TextualDatatype and the parameters are the same of the superclass

    :attr:`max_length` is 199.

    The type of ``value`` must be `str` and should match the format
    [NN] [(999)]999-9999[X99999][B99999][C any text]

    :raise: :exc:`ValueError` raised when the value does not match the expected format
    """
    def __init__(self, value, validation_level=None):

        regexp = "(\d\d\s)?(\(\d+\))?(\d+-?\d+)(X\d+)?(B\d+)?(C.+)?"
        if not re.match(regexp, value):
            raise ValueError('Invalid value for TN data')

        super(TN, self).__init__(value, 199, None, validation_level)
