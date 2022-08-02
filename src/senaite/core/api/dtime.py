# -*- coding: utf-8 -*-

import os
import time
from datetime import date
from datetime import datetime
from string import Template

import six

import pytz
from bika.lims import logger
from bika.lims.api import APIError
from DateTime import DateTime
from DateTime.DateTime import DateError
from DateTime.DateTime import SyntaxError
from DateTime.DateTime import TimeError
from Products.CMFPlone.i18nl10n import ulocalized_time
from zope.i18n import translate


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
    if is_DT(dt):
        return dt
    elif is_str(dt):
        try:
            return DateTime(dt)
        except (DateError, TimeError, SyntaxError, IndexError):
            return None
    elif is_dt(dt):
        return DateTime(dt.isoformat())
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


def get_timezone(dt, default="Etc/GMT"):
    """Get a valid pytz timezone of the datetime object

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
        if tz.startswith("GMT+0"):
            tz = tz.replace("GMT+0", "Etc/GMT")
        elif tz.startswith("GMT+"):
            tz = tz.replace("GMT+", "Etc/GMT-")
        elif tz.startswith("GMT-"):
            tz = tz.replace("GMT-", "Etc/GMT+")
        elif tz.startswith("GMT"):
            tz = tz.replace("GMT", "Etc/GMT")
    else:
        tz = default

    return tz


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
    dt = to_DT(dt)
    if not dt:
        return default

    try:
        time_str = ulocalized_time(
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
        time_str = date_to_string(dt, formatstring)
    return time_str
