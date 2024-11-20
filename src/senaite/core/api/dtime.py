# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import os
import re
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from string import Template

import six

import pytz
from bika.lims import logger
from bika.lims.api import APIError
from bika.lims.api import get_tool
from bika.lims.api import to_int
from DateTime import DateTime
from DateTime.DateTime import DateError
from DateTime.DateTime import DateTimeError
from DateTime.DateTime import SyntaxError
from DateTime.DateTime import TimeError
from zope.i18n import translate


RX_GMT = r"^(\bGMT\b|)([+-]?)(\d{1,2})"

_marker = object()


def is_str(obj):
    """Check if the given object is a string

    :param obj: arbitrary object
    :returns: True when the object is a string
    """
    return isinstance(obj, six.string_types)


def is_d(dt):
    """Check if the date is a Python `date` object

    :param dt: date to check
    :returns: True when the date is a Python `date`
    """
    return type(dt) is date


def is_dt(dt):
    """Check if the date is a Python `datetime` object

    :param dt: date to check
    :returns: True when the date is a Python `datetime`
    """
    return type(dt) is datetime


def is_DT(dt):
    """Check if the date is a Zope `DateTime` object

    :param dt: object to check
    :returns: True when the object is a Zope `DateTime`
    """
    return type(dt) is DateTime


def is_date(dt):
    """Check if the date is a datetime or DateTime object

    :param dt: date to check
    :returns: True when the object is either a datetime or DateTime
    """
    if is_str(dt):
        DT = to_DT(dt)
        return is_date(DT)
    if is_d(dt):
        return True
    if is_dt(dt):
        return True
    if is_DT(dt):
        return True
    return False


def is_timezone_naive(dt):
    """Check if the date is timezone naive

    :param dt: date to check
    :returns: True when the date has no timezone
    """
    if is_d(dt):
        return True
    elif is_DT(dt):
        return dt.timezoneNaive()
    elif is_dt(dt):
        return dt.tzinfo is None
    elif is_str(dt):
        DT = to_DT(dt)
        return is_timezone_naive(DT)
    raise APIError("Expected a date type, got '%r'" % type(dt))


def is_timezone_aware(dt):
    """Check if the date is timezone aware

    :param dt: date to check
    :returns: True when the date has a timezone
    """
    return not is_timezone_naive(dt)


def to_DT(dt):
    """Convert to DateTime

    :param dt: DateTime/datetime/date
    :returns: DateTime object
    """
    INTERNATIONAL_FMT = re.compile(
        r"^\s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.(\d{2,4})\s*"
    )
    if is_DT(dt):
        return dt
    elif is_str(dt):
        kwargs = {}
        if re.match(INTERNATIONAL_FMT, dt):
            # This will fail silently and you get a wrong date:
            # dt = DateTime("02.07.2010") # Parses like US date 02/07/2010
            # https://github.com/zopefoundation/DateTime/blob/master/src/DateTime/DateTime.py#L641-L645
            kwargs["datefmt"] = "international"
        try:
            return DateTime(dt, **kwargs)
        except (DateError, DateTimeError, TimeError):
            try:
                dt = ansi_to_dt(dt)
                return to_DT(dt)
            except ValueError:
                return None
        except (SyntaxError, IndexError):
            return None
    elif is_dt(dt):
        try:
            # We do this because isoformat() comes with the +/- utc offset at
            # the end, so it becomes easier than having to rely on tzinfo stuff
            return DateTime(dt.isoformat())
        except DateTimeError:
            return DateTime(dt)
    elif is_d(dt):
        dt = datetime(dt.year, dt.month, dt.day)
        return DateTime(dt.isoformat())
    else:
        return None


def to_dt(dt):
    """Convert to datetime

    :param dt: DateTime/datetime/date
    :returns: datetime object
    """
    if is_DT(dt):
        # get a valid pytz timezone
        tz = get_timezone(dt)
        dt = dt.asdatetime()
        if is_valid_timezone(tz):
            dt = to_zone(dt, tz)
        return dt
    elif is_str(dt):
        DT = to_DT(dt)
        return to_dt(DT)
    elif is_dt(dt):
        return dt
    elif is_d(dt):
        return datetime(dt.year, dt.month, dt.day)
    else:
        return None


def now():
    """Returns a timezone-aware datetime representing current date and time
    as defined in Zope's TZ environment variable or, if not set, from OS

    :returns: timezone-aware datetime object
    """
    return to_dt(DateTime())


def ansi_to_dt(dt):
    """The YYYYMMDD format is defined by ANSI X3.30. Therefore, 2 December 1,
    1989 would be represented as 19891201. When times are transmitted, they
    shall be represented as HHMMSS, and shall be linked to dates as specified
    by ANSI X3.43.3 Date and time together shall be specified as up to a
    14-character string: YYYYMMDD[HHMMSS]
    :param str:
    :return: datetime object
    """
    if not is_str(dt):
        raise TypeError("Type is not supported")
    if len(dt) == 8:
        date_format = "%Y%m%d"
    elif len(dt) == 14:
        date_format = "%Y%m%d%H%M%S"
    else:
        raise ValueError("No ANSI format date")
    return datetime.strptime(dt, date_format)


def to_ansi(dt, show_time=True, timezone=None):
    """Returns the date in ANSI X3.30/X4.43.3) format
    :param dt: DateTime/datetime/date
    :param show_time: if true, returns YYYYMMDDHHMMSS. YYYYMMDD otherwise
    :param timezone: if set, converts the date to the given timezone
    :returns: str that represents the datetime in ANSI format
    """
    dt = to_dt(dt)
    if dt is None:
        return None

    if timezone and is_valid_timezone(timezone):
        if is_timezone_naive(dt):
            # XXX Localize to default TZ to overcome `to_dt` inconsistency:
            #
            # - if the input value is a datetime/date type, `to_dt` does not
            #   convert to the OS's zone, even if the value is tz-naive.
            # - if the input value is a str or DateTime, `to_dt` does  convert
            #   to the system default zone.
            #
            # For instance:
            # >>> to_dt("19891201131405")
            # datetime.datetime(1989, 12, 1, 13, 14, 5, tzinfo=<StaticTzInfo 'Etc/GMT'>)
            # >>> ansi_to_dt("19891201131405")
            # datetime.datetime(1989, 12, 1, 13, 14, 5)
            #
            # That causes the following inconsistency:
            # >>> to_ansi(to_dt("19891201131405"), timezone="Pacific/Fiji")
            # 19891202011405
            # >>> to_ansi(ansi_to_dt("19891201131405"), timezone="Pacific/Fiji")
            # 19891201131405

            default_tz = get_timezone(dt)
            default_zone = pytz.timezone(default_tz)
            dt = default_zone.localize(dt)

        dt = to_zone(dt, timezone)

    ansi = "{:04d}{:02d}{:02d}".format(dt.year, dt.month, dt.day)
    if not show_time:
        return ansi
    return "{}{:02d}{:02d}{:02d}".format(ansi, dt.hour, dt.minute, dt.second)


def get_timezone(dt, default="Etc/GMT"):
    """Get a valid pytz timezone name of the datetime object

    :param dt: date object
    :returns: timezone as string, e.g. Etc/GMT or CET
    """
    tz = None
    if is_dt(dt):
        tz = dt.tzname()
    elif is_DT(dt):
        tz = dt.timezone()
    elif is_d(dt):
        tz = default

    if tz:
        # convert DateTime `GMT` to `Etc/GMT` timezones
        # NOTE: `GMT+1` get `Etc/GMT-1`!
        #
        # The special area of "Etc" is used for some administrative zones,
        # particularly for "Etc/UTC" which represents Coordinated Universal
        # Time. In order to conform with the POSIX style, those zone names
        # beginning with "Etc/GMT" have their sign reversed from the standard
        # ISO 8601 convention. In the "Etc" area, zones west of GMT have a
        # positive sign and those east have a negative sign in their name (e.g
        # "Etc/GMT-14" is 14 hours ahead of GMT).
        # --- From https://en.wikipedia.org/wiki/Tz_database#Area
        match = re.match(RX_GMT, tz)
        if match:
            groups = match.groups()
            hours = to_int(groups[2], 0)
            if not hours:
                return "Etc/GMT"

            offset = "-" if groups[1] == "+" else "+"
            tz = "Etc/GMT%s%s" % (offset, hours)
    else:
        tz = default

    return tz


def get_tzinfo(dt_tz, default=pytz.UTC):
    """Returns the valid pytz tinfo from the date or timezone name

    Returns the default timezone info if date does not have a valid timezone
    set or is TZ-naive

    :param dt: timezone name or date object to extract the tzinfo
    :type dt: str/date/datetime/DateTime
    :param: default: timezone name or pytz tzinfo object
    :returns: pytz tzinfo object, e.g. `<UTC>, <StaticTzInfo 'Etc/GMT+2'>
    :rtype: UTC/BaseTzInfo/StaticTzInfo/DstTzInfo
    """
    if is_str(default):
        default = pytz.timezone(default)
    try:
        if is_str(dt_tz):
            return pytz.timezone(dt_tz)
        tz = get_timezone(dt_tz, default=default.zone)
        return pytz.timezone(tz)
    except pytz.UnknownTimeZoneError:
        return default


def is_valid_timezone(timezone):
    """Checks if the timezone is a valid pytz/Olson name

    :param timezone: pytz/Olson timezone name
    :returns: True when the timezone is a valid zone
    """
    try:
        pytz.timezone(timezone)
        return True
    except pytz.UnknownTimeZoneError:
        return False


def get_os_timezone(default="Etc/GMT"):
    """Return the default timezone of the system

    :returns: OS timezone or default timezone
    """
    timezone = None
    if "TZ" in os.environ.keys():
        # Timezone from OS env var
        timezone = os.environ["TZ"]
    if not timezone:
        # Timezone from python time
        zones = time.tzname
        if zones and len(zones) > 0:
            timezone = zones[0]
        else:
            logger.warn(
                "Operating system\'s timezone cannot be found. "
                "Falling back to %s." % default)
            timezone = default
    if not is_valid_timezone(timezone):
        return default
    return timezone


def to_zone(dt, timezone):
    """Convert date to timezone

    Adds the timezone for timezone naive datetimes

    :param dt: date object
    :param timezone: timezone
    :returns: date converted to timezone
    """
    if is_dt(dt) or is_d(dt):
        dt = to_dt(dt)
        zone = pytz.timezone(timezone)
        if is_timezone_aware(dt):
            return dt.astimezone(zone)
        return zone.localize(dt)
    elif is_DT(dt):
        # NOTE: This shifts the time according to the TZ offset
        return dt.toZone(timezone)
    raise TypeError("Expected a date, got '%r'" % type(dt))


def to_timestamp(dt):
    """Generate a Portable Operating System Interface (POSIX) timestamp

    :param dt: date object
    :returns: timestamp in seconds
    """
    timestamp = 0
    if is_DT(dt):
        timestamp = dt.timeTime()
    elif is_dt(dt):
        timestamp = time.mktime(dt.timetuple())
    elif is_str(dt):
        DT = to_DT(dt)
        return to_timestamp(DT)
    return timestamp


def from_timestamp(timestamp):
    """Generate a datetime object from a POSIX timestamp

    :param timestamp: POSIX timestamp
    :returns: datetime object
    """
    return datetime.utcfromtimestamp(timestamp)


def to_iso_format(dt):
    """Convert to ISO format
    """
    if is_dt(dt):
        return dt.isoformat()
    elif is_DT(dt):
        return dt.ISO()
    elif is_str(dt):
        DT = to_DT(dt)
        return to_iso_format(DT)
    return None


def date_to_string(dt, fmt="%Y-%m-%d", default=""):
    """Format the date to string
    """
    if not is_date(dt):
        return default

    # NOTE: The function `is_date` evaluates also string dates as `True`.
    #       We ensure in such a case to have a `DateTime` object and leave
    #       possible `datetime` objects unchanged.
    if isinstance(dt, six.string_types):
        dt = to_DT(dt)

    try:
        return dt.strftime(fmt)
    except ValueError:
        #  Fix ValueError: year=1111 is before 1900;
        #  the datetime strftime() methods require year >= 1900

        # convert format string to be something like "${Y}-${m}-${d}"
        new_fmt = ""
        var = False
        for x in fmt:
            if x == "%":
                var = True
                new_fmt += "${"
                continue
            if var:
                new_fmt += x
                new_fmt += "}"
                var = False
            else:
                new_fmt += x

        def pad(val):
            """Add a zero if val is a single digit
            """
            return "{:0>2}".format(val)

        # Manually extract relevant date and time parts
        dt = to_DT(dt)
        data = {
            "Y": dt.year(),
            "y": dt.yy(),
            "m": dt.mm(),
            "d": dt.dd(),
            "H": pad(dt.h_24()),
            "I": pad(dt.h_12()),
            "M": pad(dt.minute()),
            "p": dt.ampm().upper(),
            "S": dt.second(),
        }

        return Template(new_fmt).safe_substitute(data)


def to_localized_time(dt, long_format=None, time_only=None,
                      context=None, request=None, default=""):
    """Convert a date object to a localized string

    :param dt: The date/time to localize
    :type dt: str/datetime/DateTime
    :param long_format: Return long date/time if True
    :type portal_type: boolean/null
    :param time_only: If True, only returns time.
    :type title: boolean/null
    :param context: The current context
    :type context: ATContentType
    :param request: The current request
    :type request: HTTPRequest object
    :returns: The formatted date as string
    :rtype: string
    """
    if not dt:
        return default

    try:
        ts = get_tool("translation_service")
        time_str = ts.ulocalized_time(
            dt, long_format, time_only, context, "senaite.core", request)
    except ValueError:
        # Handle dates < 1900

        # code taken from Products.CMFPlone.i18nl110n.ulocalized_time
        if time_only:
            msgid = "time_format"
        elif long_format:
            msgid = "date_format_long"
        else:
            msgid = "date_format_short"

        formatstring = translate(msgid, "senaite.core", {}, request)
        if formatstring == msgid:
            if msgid == "date_format_long":
                formatstring = "%Y-%m-%d %H:%M"  # 2038-01-19 03:14
            elif msgid == "date_format_short":
                formatstring = "%Y-%m-%d"  # 2038-01-19
            elif msgid == "time_format":
                formatstring = "%H:%M"  # 03:14
            else:
                formatstring = "[INTERNAL ERROR]"
        time_str = date_to_string(dt, formatstring, default=default)
    return time_str


def get_relative_delta(dt1, dt2=None):
    """Calculates the relative delta between two dates or datetimes

    If `dt2` is None, the current datetime is used.

    :param dt1: the first date/time to compare
    :type dt1: string/date/datetime/DateTime
    :param dt2: the second date/time to compare
    :type dt2: string/date/datetime/DateTime
    :returns: interval of time (e.g. `relativedelta(hours=+3)`)
    :rtype: dateutil.relativedelta
    """
    if not dt2:
        dt2 = datetime.now()

    dt1 = to_dt(dt1)
    dt2 = to_dt(dt2)
    if not all([dt1, dt2]):
        raise ValueError("No valid date or dates")

    naives = [is_timezone_naive(dt) for dt in [dt1, dt2]]
    if all(naives):
        # Both naive, no need to do anything special
        return relativedelta(dt2, dt1)

    elif is_timezone_naive(dt1):
        # From date is naive, assume same TZ as the to date
        tzinfo = get_tzinfo(dt2)
        dt1 = dt1.replace(tzinfo=tzinfo)

    elif is_timezone_naive(dt2):
        # To date is naive, assume same TZ as the from date
        tzinfo = get_tzinfo(dt1)
        dt2 = dt2.replace(tzinfo=tzinfo)

    return relativedelta(dt2, dt1)


def timedelta_to_dict(value, default=_marker):
    """Converts timedelta value to dict object

    {
        "days": 10,
        "hours": 10,
        "minutes": 10,
        "seconds": 10,
    }

    :param value: timedelta object for conversion
    :type value: timedelta
    :param value: timedelta object for conversion
    :type value: timedelta
    :returns converted timedelta as dict or default object
    :rtype: dict or default object
    """

    if not isinstance(value, timedelta):
        if default is _marker:
            raise TypeError("%r is not supported" % type(value))
        logger.warn(
            "Invalid value passed to timedelta->dict conversion. "
            "Falling back to default: %s." % default)
        return default

    # Note timedelta keeps days and seconds a part!
    return {
        "days": value.days,
        "hours": value.seconds // 3600,  # hours within a day
        "minutes": (value.seconds % 3600) // 60,  # minutes within an hour
        "seconds": value.seconds % 60,  # seconds within a minute
    }


def to_timedelta(value, default=_marker):
    """Converts dict object w/ days, hours, minutes, seconds keys to
       timedelta format

    :param value: dict object for conversion
    :type value: dict
    :returns converted timedelta
    :rtype: timedelta
    """

    if isinstance(value, timedelta):
        return value

    if not isinstance(value, dict):
        if default is _marker:
            raise TypeError("%r is not supported" % type(value))
        logger.warn(
            "Invalid value passed to dict->timedelta conversion. "
            "Falling back to default: %s." % default)
        return default

    return timedelta(
        days=to_int(value.get('days', 0), 0),
        hours=to_int(value.get('hours', 0), 0),
        minutes=to_int(value.get('minutes', 0), 0),
        seconds=to_int(value.get('seconds', 0), 0)
    )
