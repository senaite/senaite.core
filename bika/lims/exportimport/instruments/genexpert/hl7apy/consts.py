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
HL7apy - Constants
"""

#: number of expected separators
N_SEPS = 4

#: Dictionary with default encoding characters as per standard specifications
DEFAULT_ENCODING_CHARS = {
    'GROUP': '\r',
    'SEGMENT': '\r',
    'FIELD':  '|',
    'COMPONENT': '^',
    'SUBCOMPONENT': '&',
    'REPETITION': '~',
    'ESCAPE': '\\'
}

#: default hl7 version
DEFAULT_VERSION = "2.5"


class MLLP_ENCODING_CHARS(object):
    """
    MLLP encoding chars
    """
    #: Start Block
    SB = '\x0b'
    #: End Block
    EB = '\x1c'
    #: Carriage return
    CR = '\x0d'


class VALIDATION_LEVEL(object):
    """
    Allowed validation levels
    """
    #: Strict validation
    STRICT = 1
    #: Tolerant validation
    TOLERANT = 2
    # kept for backward compatibility
    QUIET = TOLERANT