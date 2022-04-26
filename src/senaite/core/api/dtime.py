# -*- coding: utf-8 -*-

import os
import time
from datetime import date
from datetime import datetime

import six

import pytz
from bika.lims import logger
from bika.lims.api import APIError
from DateTime import DateTime
from DateTime.DateTime import DateError
from DateTime.DateTime import SyntaxError
from DateTime.DateTime import TimeError


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
