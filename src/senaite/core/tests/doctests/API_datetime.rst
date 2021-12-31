SENAITE datetime API
--------------------

The datetime API provides fuctions to handle Python `datetime` and Zope's `DateTime` objects.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_datetime


Test Setup
..........

Imports:

    >>> from senaite.core.api import dtime

Define some variables:

    >>> DATEFORMAT = "%Y-%m-%d %H:%M"


Setup the test user
...................

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Check if an object is a Python `datetime`
.........................................

    >>> from datetime import datetime

    >>> dtime.is_dt(datetime.now())
    True

    >>> dtime.is_dt("2021-12-24")
    False


Check if an object is a ZOPE `DateTime`
.......................................

    >>> from DateTime import DateTime

    >>> dtime.is_DT(DateTime())
    True

    >>> dtime.is_DT("2021-12-24")
    False


Check if an object represents a date
....................................

    >>> dtime.is_date(datetime.now())
    True

    >>> dtime.is_date(DateTime())
    True

    >>> dtime.is_date("2021-12-24")
    False

    >>> dtime.is_date(object())
    False


Check if a datetime object is TZ naive
......................................

    >>> dtime.is_timezone_naive(datetime.now())
    True

    >>> dtime.is_timezone_naive(DateTime())
    False


Check if a datetime object is TZ aware
......................................

    >>> dtime.is_timezone_aware(datetime.now())
    False

    >>> dtime.is_timezone_aware(DateTime())
    True


Convert to DateTime
...................

    >>> DATE = "2021-12-24 12:00"

Timezone naive datetimes are converterd to `GMT+0`:

    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dt
    datetime.datetime(2021, 12, 24, 12, 0)

    >>> dtime.to_DT(dt)
    DateTime('2021/12/24 12:00:00 GMT+0')

    >>> DATE = "2021-08-01 12:00"

    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dt
    datetime.datetime(2021, 8, 1, 12, 0)

    >>> dtime.to_DT(dt)
    DateTime('2021/08/01 12:00:00 GMT+0')

Timezone aware datetimes are converterd to `GMT+<tzoffset>`

    >>> local_dt = dtime.to_zone(dt, "CET")
    >>> local_dt
    datetime.datetime(2021, 8, 1, 12, 0, tzinfo=<DstTzInfo 'CET' CEST+2:00:00 DST>)

    >>> dtime.to_DT(local_dt)
    DateTime('2021/08/01 12:00:00 GMT+2')


Convert to datetime
...................

    >>> dt = dtime.to_dt(DateTime())
    >>> isinstance(dt, datetime)
    True

Timezone naive `DateTime` is converted w/o timezone:

    >>> dt = DateTime(DATE)
    >>> dt
    DateTime('2021/08/01 12:00:00 GMT+0')

    >>> dtime.is_timezone_naive(dt)
    True

    >>> dtime.to_dt(dt)
    datetime.datetime(2021, 8, 1, 12, 0)

Timezone aware `DateTime` is converted with timezone.

    >>> dt = dtime.to_zone(dt, "CET")
    >>> dtime.is_timezone_naive(dt)
    False

    >>> dt
    DateTime('2021/08/01 13:00:00 GMT+1')

    >>> dtime.to_dt(dt)
    datetime.datetime(2021, 8, 1, 13, 0, tzinfo=<StaticTzInfo 'GMT+1'>)


Check if timezone is valid
..........................

    >>> dtime.is_valid_timezone("Europe/Berlin")
    True

    >>> dtime.is_valid_timezone("UTC")
    True

    >>> dtime.is_valid_timezone("CET")
    True

    >>> dtime.is_valid_timezone("CEST")
    False


Get the default timezone from the system
........................................

    >>> import os
    >>> import time

    >>> os.environ["TZ"] = "Europe/Berlin"
    >>> dtime.get_os_timezone()
    'Europe/Berlin'

    >>> os.environ["TZ"] = ""
    >>> time.tzname = ("CET", "CEST")
    >>> dtime.get_os_timezone()
    'CET'


Convert date to timezone
........................

    >>> DATE = "1970-01-01 01:00"

Convert `datetime` objects to a timezone:

    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dt_utc = dtime.to_zone(dt, "UTC")
    >>> dt_utc
    datetime.datetime(1970, 1, 1, 1, 0, tzinfo=<UTC>)

    >>> dtime.to_zone(dt_utc, "CET")
    datetime.datetime(1970, 1, 1, 2, 0, tzinfo=<DstTzInfo 'CET' CET+1:00:00 STD>)

Convert `DateTime` objects to a timezone:

    >>> DT = DateTime(DATE)
    >>> DT_utc = dtime.to_zone(DT, "UTC")
    >>> DT_utc
    DateTime('1970/01/01 01:00:00 UTC')

    >>> dtime.to_zone(DT_utc, "CET")
    DateTime('1970/01/01 02:00:00 GMT+1')


Make a POSIX timestamp
......................


    >>> DATE = "1970-01-01 01:00"
    >>> DT = DateTime(DATE)
    >>> dt = datetime.strptime(DATE, DATEFORMAT)

    >>> dtime.to_timestamp(dt)
    3600.0

    >>> dtime.to_timestamp(DT)
    3600.0
