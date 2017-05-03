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
class HL7apyException(Exception):
    """
    Base exception class for hl7apy
    """


class ParserError(HL7apyException):
    """
    Error during parsing

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.parser import parse_message
    >>> m = parse_message('NOTHL7')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ParserError: Invalid message
    """


class ValidationError(HL7apyException):
    """
    Error during validation

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.parser import parse_message
    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.validation import VALIDATION_LEVEL
    >>> msh = 'MSH|^~\&|SENDING APP|SENDING FAC|REC APP|REC FAC|20080115153000||ADT^A01^ADT_A01|' \
    '0123456789|P|2.5||||AL\\r'
    >>> evn = 'EVN||20080115153000||AAA|AAA|20080114003000\\r'
    >>> pid = 'PID|1||123-456-789^^^HOSPITAL^MR||SURNAME^NAME^A|||M|||1111 SOMEWHERE STREET^^SOMEWHERE^^^USA||' \
    '555-555-2004~444-333-222|||M\\r'
    >>> message = msh + evn + pid
    >>> parse_message(message, validation_level=VALIDATION_LEVEL.STRICT, force_validation=True)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValidationError: Missing required child ADT_A01.PV1
    """


class ValidationWarning(HL7apyException):
    """
    Warning during validation
    """


class UnsupportedVersion(HL7apyException):
    """
    Given version is not supported

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy import set_default_version
    >>> set_default_version("2.0")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    UnsupportedVersion: The version 2.0 is not supported
    """
    def __init__(self, version):
        self.version = version

    def __str__(self):
        return 'The version {0} is not supported'.format(self.version)


class ChildNotFound(HL7apyException):
    """
    Raised when a child element is not found in the HL7 reference structures for the given version

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.core import Segment, Field
    >>> s = Segment('MSH')
    >>> s.unknown = Field()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ChildNotFound: No child named UNKNOWN
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'No child named {0}'.format(self.name)


class ChildNotValid(HL7apyException):
    """
    Raised when you try to assign an unexpected child to an :class:`Element <hl7apy.core.Element>`

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.core import Segment, Field
    >>> s = Segment('PID', validation_level=1)
    >>> s.pid_1 = Field('PID_34')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ChildNotValid: <Field PID_34 (LAST_UPDATE_FACILITY) of type HD> is not a valid child for PID_1
    """
    def __init__(self, child, parent):
        self.child = child
        self.parent = parent

    def __str__(self):
        return '{0} is not a valid child for {1}'.format(self.child, self.parent)


class UnknownValidationLevel(HL7apyException):
    """
    Raised when the validation_level specified is not valid

    It should be one of those defined in :class:`VALIDATION_LEVEL <hl7apy.consts.VALIDATION_LEVEL>`.

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy import set_default_validation_level
    >>> set_default_validation_level(3)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    UnknownValidationLevel
    """


class OperationNotAllowed(HL7apyException):
    """
    Generic exception raised when something is not allowed

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.core import Segment
    >>> s = Segment()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    OperationNotAllowed: Cannot instantiate an unknown Segment
    """


class MaxChildLimitReached(HL7apyException):
    """
    Raised when a child cannot be added to an instance of :class:`Element <hl7apy.core.Element>`
    since the :class:`Element <hl7apy.core.Element>` has already reached the maximum number
    of children allowed for the given child type (e.g. a :class:`Message <hl7apy.core.Message>` should have
    at most 1 MSH segment)

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.core import Message, Segment
    >>> m = Message("OML_O33", validation_level=1)
    >>> m.add(Segment('MSH'))  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    MaxChildLimitReached: Cannot add <Segment MSH>: max limit (1) reached for <Message OML_O33>
    """
    def __init__(self, parent, child, limit):
        self.parent = parent
        self.child = child
        self.limit = limit

    def __str__(self):
        return 'Cannot add {0}: max limit ({1}) reached for {2}'.format(self.child, self.limit, self.parent)


class MaxLengthReached(HL7apyException):
    """
    Value length exceeds its datatype :attr:`max_length`.

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.v2_5 import get_base_datatypes
    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.consts import VALIDATION_LEVEL
    >>> SI = get_base_datatypes()['SI']
    >>> st = SI(value=11111, validation_level=VALIDATION_LEVEL.STRICT)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    MaxLengthReached: The value 11111 exceed the max length: 4
    """
    def __init__(self, value, limit):
        self.value = value
        self.limit = limit

    def __str__(self):
        return 'The value {0} exceed the max length: {1}'.format(self.value, self.limit)


class InvalidName(HL7apyException):
    """
    Raised if the reference for the given class/name has not been found

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.core import Message
    >>> Message('Unknown')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    InvalidName: Invalid name for Message: UNKNOWN
    """
    def __init__(self, cls, name):
        self.cls = cls
        self.name = name

    def __str__(self):
        return 'Invalid name for {0}: {1}'.format(self.cls, self.name)


class InvalidDataType(HL7apyException):
    """
    Raised when the currently used HL7 version does not support the given datatype

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.factories import datatype_factory
    >>> datatype_factory('TN', '11 123456', version="2.3") #doctest: +ELLIPSIS
    <hl7apy.base_datatypes.TN object at 0x...>
    >>> datatype_factory('TN', '11 123456', version="2.5")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    InvalidDataType: The datatype TN is not available for the given HL7 version
    """
    def __init__(self, datatype):
        self.datatype = datatype

    def __str__(self):
        return "The datatype {0} is not available for the given HL7 version".format(self.datatype)


class InvalidHighlightRange(HL7apyException):
    """
    Raised when the specified highlight range is not valid

    For a description of highlight range see :class:`hl7apy.base_datatypes.TextualDataType`

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.v2_5 import ST
    >>> s = ST(value='some useful information', highlights=((5, 3),))
    >>> s.to_er7()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    InvalidHighlightRange: Invalid highlight range: 5 - 3
    """
    def __init__(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __str__(self):
        return 'Invalid highlight range: {0} - {1}'.format(self.lower_bound, self.upper_bound)


class InvalidDateFormat(HL7apyException):
    """
    Raised when the output format for a :class:`hl7apy.base_datatypes.DateTimeDataType` is not valid

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.v2_5 import DTM
    >>> DTM(value='10102013', out_format="%d%m%Y")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    InvalidDateFormat: Invalid date format: %d%m%Y
    """
    def __init__(self, out_format):
        self.format = out_format

    def __str__(self):
        return 'Invalid date format: {0}'.format(self.format)


class InvalidDateOffset(HL7apyException):
    """
    Raised when the offset for a :class:`TM` or :class:`hl7apy.base_datatypes.DTM` is not valid

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.v2_5 import DTM
    >>> DTM(value='20131010', out_format="%Y%m%d", offset='+1300')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    InvalidDateOffset: Invalid date offset: +1300
    """
    def __init__(self, offset):
        self.offset = offset

    def __str__(self):
        return 'Invalid date offset: {0}'.format(self.offset)


class InvalidMicrosecondsPrecision(HL7apyException):
    """
    Raised when the microseconds precision of a TM or DTM oject is not between 1 and 4

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.v2_5 import get_base_datatypes
    >>> DTM = get_base_datatypes()['DTM']
    >>> DTM(value='20131010', microsec_precision=5)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    InvalidMicrosecondsPrecision: Invalid microseconds precision. It must be between 1 and 4
    """

    def __str__(self):
        return 'Invalid microseconds precision. It must be between 1 and 4'


class InvalidEncodingChars(HL7apyException):
    """
    Raised when the encoding chars specified is not a correct set of HL7 encoding chars

    >>> from bika.lims.exportimport.instruments.genexpert.hl7apy.core import Message
    >>> encoding_chars = {'GROUP': '\\r', 'SEGMENT': '\\r', 'COMPONENT': '^', \
                          'SUBCOMPONENT': '&', 'REPETITION': '~', 'ESCAPE': '\\\\'}
    >>> m = Message('ADT_A01', encoding_chars=encoding_chars)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    InvalidEncodingChars: Missing required encoding chars
    """
    def __str__(self):
        return self.message if self.message else 'Invalid encoding chars'


class MessageProfileNotFound(HL7apyException):
    """
    Raised when the structure for a message is not found in the message profile specified
    """
    def __str__(self):
        return 'Message profile not found for the specified message'

if __name__ == '__main__':

    import doctest
    doctest.testmod()
