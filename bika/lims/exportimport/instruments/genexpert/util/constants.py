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


STX = '02'.decode('hex')
ETB = '17'.decode('hex')
SB =  '0b'.decode('hex')
EB =  '1c'.decode('hex')
CR = '0d'.decode('hex')
EOT = '04'.decode('hex')
ACK = '06'.decode('hex')
ENQ = '05'.decode('hex')
ETX = '03'.decode('hex')
NAK = '15'.decode('hex')
LF  = '0a'.decode('hex')

#: ASTM specification base encoding.
ENCODING = 'latin-1'

#: CR + LF shortcut.
CRLF = CR + LF
#: Message records delimiter.
RECORD_SEP    = b'\x0D' # \r #
#: Record fields delimiter.
FIELD_SEP     = b'\x7C' # |  #
#: Delimeter for repeated fields.
REPEAT_SEP    = b'\x5C' # \  #
#: Field components delimiter.
COMPONENT_SEP = b'\x5E' # ^  #
#: Date escape token.
ESCAPE_SEP    = b'\x26' # &  #

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