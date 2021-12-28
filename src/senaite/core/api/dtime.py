# -*- coding: utf-8 -*-

import os
from datetime import datetime
from time import tzname

import pytz
from bika.lims import logger
from DateTime import DateTime


def is_dt(dt):
    """Check if the date is a Python `datetime` object

    :param dt: date to check
    :returns: True when the date is a Python `datetime`
    """
    return isinstance(dt, datetime)


def is_DT(dt):
    """Check if the date is a Zope `DateTime` object

    :param dt: object to check
    :returns: True when the object is a Zope `DateTime`
    """
    return isinstance(dt, DateTime)


def is_date(dt):
    """Check if the date is a datetime or DateTime object

    :param dt: date to check
    :returns: True when the object is either a datetime or DateTime
    """
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
    if is_DT(dt):
        return dt.timezoneNaive()
    elif is_dt(dt):
        return dt.tzinfo is None
    raise TypeError("Expected a date, got '%r'" % type(dt))


def is_timezone_aware(dt):
    """Check if the date is timezone aware

    :param dt: date to check
    :returns: True when the date has a timezone
    """
    return not is_timezone_naive(dt)


def dt_to_DT(dt):
    """Convert datetime to DateTime

    :param dt: datetime object
    :returns: DateTime object
    """
    if is_DT(dt):
        return dt
    elif is_dt(dt):
        return DateTime(dt)
    raise TypeError("Expected datetime, got '%r'" % type(dt))


def DT_to_dt(dt):
    """Convert DateTime to datetime

    :param dt: DateTime object
    :returns: datetime object
    """
    if is_DT(dt):
        return dt.asdatetime()
    elif is_dt(dt):
        return dt
    raise TypeError("Expected DateTime, got '%r'" % type(dt))


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


def get_os_timezone():
    """Return the default timezone of the system

    :returns: OS timezone or UTC
    """
    fallback = "UTC"
    timezone = None
    if "TZ" in os.environ.keys():
        # Timezone from OS env var
        timezone = os.environ["TZ"]
    if not timezone:
        # Timezone from python time
        zones = tzname
        if zones and len(zones) > 0:
            timezone = zones[0]
        else:
            # Default fallback = UTC
            logger.warn(
                "Operating system\'s timezone cannot be found. "
                "Falling back to UTC.")
            timezone = fallback
    if not is_valid_timezone(timezone):
        return fallback
    return timezone


def to_zone(dt, timezone):
    """Convert date to timezone

    Adds the timezone for timezone naive datetimes

    :param dt: date object
    :param timezone: timezone
    :returns: date converted to timezone
    """
    if is_dt(dt):
        zone = pytz.timezone(timezone)
        if is_timezone_aware(dt):
            return dt.astimezone(zone)
        return zone.localize(dt)
    if is_DT(dt):
        return dt.toZone(timezone)
