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
import re
from datetime import datetime


def check_date(value):
    """
    Checks that the value is a valid HL7 date

    :param value: the value to check
    :return: `True` if the value is correct, `False` otherwise
    """
    try:
        get_date_info(value)
    except ValueError:
        return False
    return True


def check_datetime(value):
    """
    Checks that the value is a valid HL7 datetime

    :param value: the value to check
    :return: `True` if the value is correct, `False` otherwise
    """

    try:
        get_datetime_info(value)
    except ValueError:
        return False
    return True


def check_timestamp(value):
    """
    Checks that the value is a valid HL7 timestamp

    :param value: the value to check
    :return: `True` if the value is correct, `False` otherwise
    """
    try:
        get_timestamp_info(value)
    except ValueError:
        return False
    return True


def get_date_info(value):
    """
    Returns the datetime object and the format of the date in input

    :type value: `str`
    """
    fmt = _get_date_format(value)
    dt_value = _datetime_obj_factory(value, fmt)
    return dt_value, fmt


def get_timestamp_info(value):
    """
    Returns the datetime object, the format, the offset and the microsecond of the timestamp in input

    :type value: `str`
    """
    value, offset = _split_offset(value)
    fmt, microsec = _get_timestamp_format(value)
    dt_value = _datetime_obj_factory(value, fmt)
    return dt_value, fmt, offset, microsec


def get_datetime_info(value):
    """
    Returns the datetime object, the format, the offset and the microsecond of the datetime in input

    :type value: `str`
    """
    date_value, offset = _split_offset(value)
    date_format = _get_date_format(date_value[:8])

    try:
        timestamp_form, microsec = _get_timestamp_format(date_value[8:])
    except ValueError:
        if not date_value[8:]:  # if it's empty
            timestamp_form, microsec = '', 4
        else:
            raise ValueError('{0} is not an HL7 valid date value'.format(value))

    fmt = '{0}{1}'.format(date_format, timestamp_form)
    dt_value = _datetime_obj_factory(date_value, fmt)
    return dt_value, fmt, offset, microsec


def _split_offset(value):
    offset = re.search('\d*((-|\+)(1[0-2]|0[0-9])([0-5][0-9]))$', value)
    if offset:
        offset = offset.groups()[0]
        return value.replace(offset, ''), offset
    return value, ''


def _get_date_format(value):
    if len(value) == 4:
        fmt = '%Y'
    elif len(value) == 6:
        fmt = '%Y%m'
    elif len(value) == 8:
        fmt = '%Y%m%d'
    else:
        raise ValueError('{0} is not an HL7 valid date value'.format(value))

    return fmt


def _get_timestamp_format(value):
    microsec = 4
    if len(value) == 2:
        fmt = '%H'
    elif len(value) == 4:
        fmt = '%H%M'
    elif len(value) == 6:
        fmt = '%H%M%S'
    elif 8 <= len(value) <= 11 and value[6] == '.':
        fmt = '%H%M%S.%f'
        microsec = len(value) - 7  # it gets the precision of the microseconds part
    else:
        raise ValueError('{0} is not an HL7 valid date value'.format(value))

    return fmt, microsec


def _datetime_obj_factory(value, fmt):
    try:
        dt_value = datetime.strptime(value, fmt)
    except ValueError:
        raise ValueError('{0} is not an HL7 valid date value'.format(value))
    return dt_value


def iteritems(d):
    if hasattr(d, 'iteritems'):
        return d.iteritems()
    else:
        return d.items()
