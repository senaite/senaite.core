SENAITE datetime API
--------------------

The datetime API provides fuctions to handle Python `datetime` and Zope's `DateTime` objects.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_datetime


Test Setup
..........

Imports:

    >>> from bika.lims.api import get_tool
    >>> from senaite.core.api import dtime

Define some variables:

    >>> DATEFORMAT = "%Y-%m-%d %H:%M"

Test fixture:

    >>> import os
    >>> os.environ["TZ"] = "CET"


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


Check if an object is a Python `date`
.....................................

    >>> from datetime import date

    >>> dtime.is_d(date.today())
    True

    >>> dtime.is_d("2022-01-01")
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

    >>> dtime.is_date(date.today())
    True

    >>> dtime.is_date(datetime.now())
    True

    >>> dtime.is_date(DateTime())
    True

    >>> dtime.is_date("2021-12-24")
    True

    >>> dtime.is_date("2021-12-24T12:00:00")
    True

    >>> dtime.is_date("2021-12-24T12:00:00+01:00")
    True

    >>> dtime.is_date("Hello World")
    False

    >>> dtime.is_date(object())
    False


Check if a datetime object is TZ naive
......................................

    >>> dtime.is_timezone_naive(date.today())
    True

    >>> dtime.is_timezone_naive(datetime.now())
    True

    >>> dtime.is_timezone_naive(DateTime())
    False

    >>> dtime.is_timezone_naive("2021-12-24")
    True

    >>> dtime.is_timezone_naive("2021-12-24T12:00:00")
    True

    >>> dtime.is_timezone_naive("2021-12-24T12:00:00+01:00")
    False


Check if a datetime object is TZ aware
......................................

    >>> dtime.is_timezone_aware(date.today())
    False

    >>> dtime.is_timezone_aware(datetime.now())
    False

    >>> dtime.is_timezone_aware(DateTime())
    True

    >>> dtime.is_timezone_aware("2021-12-24")
    False

    >>> dtime.is_timezone_aware("2021-12-24T12:00:00")
    False

    >>> dtime.is_timezone_aware("2021-12-24T12:00:00+01:00")
    True


Convert to DateTime
...................

    >>> DATE = "2021-12-24 12:00"

Timezone naive datetimes are converterd to `GMT+0`:

    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dt
    datetime.datetime(2021, 12, 24, 12, 0)

    >>> dtime.to_DT(DATE)
    DateTime('2021/12/24 12:00:00 GMT+0')

    >>> dtime.to_DT(dt)
    DateTime('2021/12/24 12:00:00 GMT+0')

    >>> DATE = "2021-08-01 12:00"

    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dt
    datetime.datetime(2021, 8, 1, 12, 0)

    >>> dtime.to_DT(dt)
    DateTime('2021/08/01 12:00:00 GMT+0')

    >>> dtime.to_DT(date.fromtimestamp(0))
    DateTime('1970/01/01 00:00:00 GMT+0')

International format is automatically detected and supported:

    >>> dtime.to_DT("02.07.2010 17:50:34 GMT+2")
    DateTime('2010/07/02 17:50:34 GMT+2')

    >>> dtime.to_DT("13.12.2018 17:50:34 GMT+1")
    DateTime('2018/12/13 17:50:34 GMT+1')

    >>> dtime.to_DT("12.13.2018 17:50:34 GMT+1")
    DateTime('2018/12/13 17:50:34 GMT+1')

Timezone aware datetimes are converterd to `GMT+<tzoffset>`

    >>> local_dt = dtime.to_zone(dt, "CET")
    >>> local_dt
    datetime.datetime(2021, 8, 1, 12, 0, tzinfo=<DstTzInfo 'CET' CEST+2:00:00 DST>)

    >>> dtime.to_DT(local_dt)
    DateTime('2021/08/01 12:00:00 GMT+2')

Old dates with obsolete timezones (e.g. LMT) are converted as well

    >>> old_dt = datetime(1682, 8, 16, 2, 44, 52)
    >>> old_dt = dtime.to_zone(old_dt, "Pacific/Port_Moresby")
    >>> old_dt
    datetime.datetime(1682, 8, 16, 2, 44, 52, tzinfo=<DstTzInfo 'Pacific/Port_Moresby' LMT+9:49:00 STD>)
    >>> old_dt.utcoffset().total_seconds()
    35340.0
    >>> old_DT = dtime.to_DT(old_dt)
    >>> old_DT
    DateTime('1682/08/16 02:44:52 Pacific/Port_Moresby')
    >>> old_DT.tzoffset()
    35340

The function returns `None` when the conversion cannot be done:

    >>> dtime.to_DT(None) is None
    True

    >>> dtime.to_DT(object) is None
    True

    >>> dtime.to_DT("Not a date") is None
    True

    >>> dtime.to_DT("2025-13-01") is None
    True

    >>> dtime.to_DT("2024-02-25 12:00 POP+2") is None
    True

    >>> dtime.to_DT("0007-02-27T00:00:00-04:24") is None
    True

Convert to datetime
...................

    >>> dt = dtime.to_dt(DateTime())
    >>> isinstance(dt, datetime)
    True

Timezone naive `DateTime` is converted with `Etc/GMT` timezone:

    >>> dt = DateTime(DATE)
    >>> dt
    DateTime('2021/08/01 12:00:00 GMT+0')

    >>> dtime.is_timezone_naive(dt)
    True

    >>> dtime.to_dt(dt)
    datetime.datetime(2021, 8, 1, 12, 0, tzinfo=<StaticTzInfo 'Etc/GMT'>)

Timezone aware `DateTime` is converted with timezone.

    >>> dt = dtime.to_zone(dt, "CET")
    >>> dtime.is_timezone_naive(dt)
    False

    >>> dt
    DateTime('2021/08/01 13:00:00 GMT+1')

    >>> dtime.to_dt(dt)
    datetime.datetime(2021, 8, 1, 13, 0, tzinfo=<StaticTzInfo 'Etc/GMT-1'>)

The function returns `None` when the conversion cannot be done:

    >>> dtime.to_dt(None) is None
    True

    >>> dtime.to_dt(object) is None
    True

    >>> dtime.to_dt("Not a date") is None
    True

    >>> dtime.to_dt("2025-13-01") is None
    True

    >>> dtime.to_dt("2024-02-25 12:00 POP+2") is None
    True

    >>> dtime.to_dt("0007-02-27T00:00:00-04:24") is None
    True

Get the timezone
................

Get the timezone from `DateTime` objects:

    >>> dtime.get_timezone(DateTime("2022-02-25"))
    'Etc/GMT'

    >>> dtime.get_timezone(DateTime("2022-02-25 12:00 GMT+2"))
    'Etc/GMT-2'

    >>> dtime.get_timezone(DateTime("2022-02-25 12:00 GMT-2"))
    'Etc/GMT+2'


Get the timezone from `datetime.datetime` objects:

    >>> DATE = "2021-12-24 12:00"
    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dtime.get_timezone(dt)
    'Etc/GMT'

    >>> dtime.get_timezone(dtime.to_zone(dt, "Europe/Berlin"))
    'CET'

Get the timezone from `datetime.date` objects:

    >>> dtime.get_timezone(dt.date)
    'Etc/GMT'

For consistency reasons, `GMT` timezones are always converted to `Etc/GMT`:

    >>> DT = DateTime('2024/11/06 15:11:20.956914 GMT+1')
    >>> DT.timezone()
    'GMT+1'

    >>> dtime.get_timezone(DT)
    'Etc/GMT-1'

Even for `datetime` objects:

    >>> dt = DT.asdatetime()
    >>> dt.tzname()
    'GMT+0100'

    >>> dtime.get_timezone(dt)
    'Etc/GMT-1'

    >>> dt = dtime.to_dt(DT)
    >>> dt.tzname()
    '+01'

    >>> dtime.get_timezone(dt)
    'Etc/GMT-1'

We can even get the obsolete timezone that was applying to an old date:

    >>> old_dt = datetime(1682, 8, 16, 2, 44, 54)
    >>> old_dt = dtime.to_zone(old_dt, "Pacific/Port_Moresby")
    >>> dtime.get_timezone(old_dt)
    'LMT'

Get the timezone info
.....................

Get the timezone info from TZ name:

    >>> dtime.get_tzinfo("Etc/GMT")
    <StaticTzInfo 'Etc/GMT'>

    >>> dtime.get_tzinfo("Pacific/Fiji")
    <DstTzInfo 'Pacific/Fiji' LMT+11:56:00 STD>

    >>> dtime.get_tzinfo("UTC")
    <UTC>

Get the timezone info from `DateTime` objects:

    >>> dtime.get_tzinfo(DateTime("2022-02-25"))
    <StaticTzInfo 'Etc/GMT'>

    >>> dtime.get_tzinfo(DateTime("2022-02-25 12:00 GMT+2"))
    <StaticTzInfo 'Etc/GMT-2'>

    >>> dtime.get_tzinfo(DateTime("2022-02-25 12:00 GMT-2"))
    <StaticTzInfo 'Etc/GMT+2'>

Get the timezone info from `datetime.datetime` objects:

    >>> DATE = "2021-12-24 12:00"
    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dtime.get_tzinfo(dt)
    <UTC>

    >>> dtime.get_tzinfo(dtime.to_zone(dt, "Europe/Berlin"))
    <DstTzInfo 'CET' CET+1:00:00 STD>

Get the timezone info from `datetime.date` objects:

    >>> dtime.get_tzinfo(dt.date)
    <UTC>

Getting the timezone info from a naive date returns default timezone info:

    >>> dt_naive = dt.replace(tzinfo=None)
    >>> dtime.get_tzinfo(dt_naive)
    <UTC>

    >>> dtime.get_tzinfo(dt_naive, default="Pacific/Fiji")
    <DstTzInfo 'Pacific/Fiji' LMT+11:56:00 STD>

We can use a timezone info as the default parameter as well:

    >>> dtime.get_tzinfo(dt_naive, default=dtime.pytz.UTC)
    <UTC>

Default can also be a timezone name:

    >>> dtime.get_tzinfo(dt_naive, default="America/Port_of_Spain")
    <DstTzInfo 'America/Port_of_Spain' LMT-1 day, 19:36:00 STD>

And an error is rised if default is not a valid timezone, even if the date
passed-in is valid:

    >>> dtime.get_tzinfo(dt_naive, default="Atlantida")
    Traceback (most recent call last):
    ...
    UnknownTimeZoneError: 'Atlantida'


Check if timezone is valid
..........................

    >>> dtime.is_valid_timezone("Etc/GMT-1")
    True

    >>> dtime.is_valid_timezone("Etc/GMT-0100")
    False

    >>> dtime.is_valid_timezone("Europe/Berlin")
    True

    >>> dtime.is_valid_timezone("UTC")
    True

    >>> dtime.is_valid_timezone("CET")
    True

    >>> dtime.is_valid_timezone("CEST")
    False

    >>> dtime.is_valid_timezone("LMT")
    False


Get the default timezone from the system
........................................

    >>> import os
    >>> import time

    >>> os.environ["TZ"] = "Europe/Berlin"
    >>> dtime.get_os_timezone()
    'Europe/Berlin'

    >>> os.environ["TZ"] = ""
    >>> dtime.time.tzname = ("CET", "CEST")
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

Convert `date` objects to a timezone (converts to `datetime`):

    >>> d = date.fromordinal(dt.toordinal())
    >>> d_utc = dtime.to_zone(d, "UTC")
    >>> d_utc
    datetime.datetime(1970, 1, 1, 0, 0, tzinfo=<UTC>)

Convert `DateTime` objects to a timezone:

    >>> DT = DateTime(DATE)
    >>> DT_utc = dtime.to_zone(DT, "UTC")
    >>> DT_utc
    DateTime('1970/01/01 01:00:00 UTC')

    >>> dtime.to_zone(DT_utc, "CET")
    DateTime('1970/01/01 02:00:00 GMT+1')


Get the current datetime (with timezone)
........................................

Python's `datetime.now()` returns a timezone-naive datetime object, whereas
Zope's DateTime() returns a timezone-aware DateTime object. This difference
can lead to inconsistencies when converting and comparing dates if not
carefully managed. The `dtime.now(timezone)` function provides the current
datetime with the timezone defined in Zope's TZ environment variable, like
Zope's `DateTime()` does. This function is strongly recommended over
`datetime.now()` except in cases where a timezone-naive datetime is explicitly
needed.

    >>> now_dt = dtime.now()
    >>> now_DT = DateTime()
    >>> now_dt.utcoffset().seconds == now_DT.tzoffset()
    True

    >>> ansi = dtime.to_ansi(now_dt)
    >>> dtime.to_ansi(now_DT) == ansi
    True

    >>> dtime.to_ansi(dtime.to_dt(now_DT)) == ansi
    True

    >>> dtime.to_ansi(dtime.to_DT(now_dt)) == ansi
    True


Make a POSIX timestamp
......................


    >>> DATE = "1970-01-01 01:00"
    >>> DT = DateTime(DATE)
    >>> dt = datetime.strptime(DATE, DATEFORMAT)

    >>> dtime.to_timestamp(DATE)
    3600.0

    >>> dtime.to_timestamp(dt)
    3600.0

    >>> dtime.to_timestamp(DT)
    3600.0

    >>> dtime.from_timestamp(dtime.to_timestamp(dt)) == dt
    True


Convert to ISO format
.....................

    >>> DATE = "2021-08-01 12:00"
    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dt_local = dtime.to_zone(dt, "CET")
    >>> dt_local
    datetime.datetime(2021, 8, 1, 12, 0, tzinfo=<DstTzInfo 'CET' CEST+2:00:00 DST>)

    >>> dtime.to_iso_format(DATE)
    '2021-08-01T12:00:00'

    >>> dtime.to_iso_format(dt_local)
    '2021-08-01T12:00:00+02:00'

    >>> dtime.to_iso_format(dtime.to_DT(dt_local))
    '2021-08-01T12:00:00+02:00'


Convert date to string
......................


Check with valid date:

    >>> DATE = "2022-08-01 12:00"
    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dtime.date_to_string(dt)
    '2022-08-01'

    >>> dtime.date_to_string(dt, fmt="%H:%M")
    '12:00'

    >>> dtime.date_to_string(dt, fmt="%Y-%m-%dT%H:%M")
    '2022-08-01T12:00'

Check if the `ValueError: strftime() methods require year >= 1900` is handled gracefully:

    >>> DATE = "1010-11-12 22:23"
    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dtime.date_to_string(dt)
    '1010-11-12'

    >>> dtime.date_to_string(dt, fmt="%H:%M")
    '22:23'

    >>> dtime.date_to_string(dt, fmt="%Y-%m-%dT%H:%M")
    '1010-11-12T22:23'

    >>> dtime.date_to_string(dt, fmt="%Y-%m-%d %H:%M")
    '1010-11-12 22:23'

    >>> dtime.date_to_string(dt, fmt="%Y/%m/%d %H:%M")
    '1010/11/12 22:23'

Check the same with `DateTime` objects:

    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> DT = dtime.to_DT(dt)
    >>> dtime.date_to_string(DT)
    '1010-11-12'

    >>> dtime.date_to_string(DT, fmt="%H:%M")
    '22:23'

    >>> dtime.date_to_string(DT, fmt="%Y-%m-%dT%H:%M")
    '1010-11-12T22:23'

    >>> dtime.date_to_string(DT, fmt="%Y-%m-%d %H:%M")
    '1010-11-12 22:23'

    >>> dtime.date_to_string(DT, fmt="%Y/%m/%d %H:%M")
    '1010/11/12 22:23'

Check paddings in hour/minute:

    >>> DATE = "2022-08-01 01:02"
    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dtime.date_to_string(dt, fmt="%Y-%m-%d %H:%M")
    '2022-08-01 01:02'

    >>> DATE = "1755-08-01 01:02"
    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dtime.date_to_string(dt, fmt="%Y-%m-%d %H:%M")
    '1755-08-01 01:02'

Check 24h vs 12h format:

    >>> DATE = "2022-08-01 23:01"
    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dtime.date_to_string(dt, fmt="%Y-%m-%d %I:%M %p")
    '2022-08-01 11:01 PM'

    >>> DATE = "1755-08-01 23:01"
    >>> dt = datetime.strptime(DATE, DATEFORMAT)
    >>> dtime.date_to_string(dt, fmt="%Y-%m-%d %I:%M %p")
    '1755-08-01 11:01 PM'


Localization
............

Values returned by TranslationService and dtime's ulocalized_time are
consistent:

    >>> ts = get_tool("translation_service")
    >>> dt = "2022-12-14"
    >>> ts_dt = ts.ulocalized_time(dt, long_format=True, domain="senaite.core")
    >>> dt_dt = dtime.to_localized_time(dt, long_format=True)
    >>> ts_dt == dt_dt
    True

    >>> dt = datetime(2022,12,14)
    >>> ts_dt = ts.ulocalized_time(dt, long_format=True, domain="senaite.core")
    >>> dt_dt = dtime.to_localized_time(dt, long_format=True)
    >>> ts_dt == dt_dt
    True

    >>> dt = DateTime(2022,12,14)
    >>> ts_dt = ts.ulocalized_time(dt, long_format=True, domain="senaite.core")
    >>> dt_dt = dtime.to_localized_time(dt, long_format=True)
    >>> ts_dt == dt_dt
    True

But when a date with a year before 1900 is used, dtime's does fallback to
standard ISO format, while TranslationService fails:

    >>> dt = "1889-12-14"
    >>> ts.ulocalized_time(dt, long_format=True, domain="senaite.core")
    Traceback (most recent call last):
    ...
    ValueError: year=1889 is before 1900; the datetime strftime() methods require year >= 1900

    >>> dtime.to_localized_time(dt, long_format=True)
    '1889-12-14 00:00'

    >>> dt = datetime(1889,12,14)
    >>> ts.ulocalized_time(dt, long_format=True, domain="senaite.core")
    Traceback (most recent call last):
    ...
    ValueError: year=1889 is before 1900; the datetime strftime() methods require year >= 1900

    >>> dtime.to_localized_time(dt, long_format=True)
    '1889-12-14 00:00'

    >>> dt = DateTime(1889,12,14)
    >>> ts.ulocalized_time(dt, long_format=True, domain="senaite.core")
    Traceback (most recent call last):
    ...
    ValueError: year=1889 is before 1900; the datetime strftime() methods require year >= 1900

    >>> dtime.to_localized_time(dt, long_format=True)
    '1889-12-14 00:00'


Support for ANSI X3.30 and ANSI X3.43.3
.......................................

The YYYYMMDD format is defined by ANSI X3.30. Therefore 2 December 1, 1989
would be represented as 19891201. When times are transmitted (ASTM), they
shall be represented as HHMMSS, and shall be linked to dates as specified by
ANSI X3.43.3 Date and time together shall be specified as up to a 14-character
string (YYYYMMDD[HHMMSS]

    >>> dt = "19891201"
    >>> dtime.ansi_to_dt(dt)
    datetime.datetime(1989, 12, 1, 0, 0)

    >>> dtime.to_DT(dt)
    DateTime('1989/12/01 00:00:00 GMT+0')

    >>> dt = "19891201131405"
    >>> dtime.ansi_to_dt(dt)
    datetime.datetime(1989, 12, 1, 13, 14, 5)

    >>> dtime.to_DT(dt)
    DateTime('1989/12/01 13:14:05 GMT+0')

    >>> dt = "17891201131405"
    >>> dtime.ansi_to_dt(dt)
     datetime.datetime(1789, 12, 1, 13, 14, 5)

    >>> dtime.to_DT(dt)
    DateTime('1789/12/01 13:14:05 GMT+0')

    >>> dt = "17891201132505"
    >>> dtime.ansi_to_dt(dt)
    datetime.datetime(1789, 12, 1, 13, 25, 5)

    >>> dtime.to_DT(dt)
    DateTime('1789/12/01 13:25:05 GMT+0')

    >>> # No ANSI format
    >>> dt = "230501"
    >>> dtime.ansi_to_dt(dt)
    Traceback (most recent call last):
    ...
    ValueError: No ANSI format date

    >>> # Month 13
    >>> dt = "17891301132505"
    >>> dtime.ansi_to_dt(dt)
    Traceback (most recent call last):
    ...
    ValueError: unconverted data remains: 5

    >>> # Month 2, day 30
    >>> dt = "20030230123408"
    >>> dtime.ansi_to_dt(dt)
    Traceback (most recent call last):
    ...
    ValueError: day is out of range for month

    >>> dtime.to_DT(dt) is None
    True

We can also the other way round conversion. Simply giving a date in ant valid
string format:

    >>> dt = "1989-12-01"
    >>> dtime.to_ansi(dt, show_time=False)
    '19891201'

    >>> dtime.to_ansi(dt, show_time=True)
    '19891201000000'

    >>> dt = "19891201"
    >>> dtime.to_ansi(dt, show_time=False)
    '19891201'

    >>> dtime.to_ansi(dt, show_time=True)
    '19891201000000'

Or using datetime or DateTime as the input parameter:

    >>> dt = "19891201131405"
    >>> dt = dtime.ansi_to_dt(dt)
    >>> dtime.to_ansi(dt, show_time=False)
    '19891201'

    >>> dtime.to_ansi(dt, show_time=True)
    '19891201131405'

    >>> DT = dtime.to_DT(dt)
    >>> dtime.to_ansi(DT, show_time=False)
    '19891201'

    >>> dtime.to_ansi(DT, show_time=True)
    '19891201131405'

We even suport dates that are long before epoch:

    >>> min_date = dtime.datetime.min
    >>> min_date
    datetime.datetime(1, 1, 1, 0, 0)

    >>> dtime.to_ansi(min_date)
    '00010101000000'

Or long after epoch:

    >>> max_date = dtime.datetime.max
    >>> max_date
    datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)

    >>> dtime.to_ansi(max_date)
    '99991231235959'

Still, invalid dates return None:

    >>> # Month 13
    >>> dt = "17891301132505"
    >>> dtime.to_ansi(dt) is None
    True

    >>> # Month 2, day 30
    >>> dt = "20030230123408"
    >>> dtime.to_ansi(dt) is None
    True

We can also specify the timezone. Since `to_ansi` relies on `to_dt` to convert
the input value to a valid datetime, naive datetime is localized to OS`s
default timezone before the hours shift:

    >>> dtime.to_ansi("1989-12-01")
    '19891201000000'

    >>> dtime.to_ansi("1989-12-01", timezone="Pacific/Fiji")
    '19891201120000'

    >>> dt = dtime.to_dt("19891201131405")
    >>> dtime.to_ansi(dt)
    '19891201131405'

    >>> dtime.to_ansi(dt, timezone="Pacific/Fiji")
    '19891202011405'

    >>> dt = dtime.ansi_to_dt("19891201131405")
    >>> dtime.to_ansi(dt)
    '19891201131405'

    >>> dtime.to_ansi(dt, timezone="Pacific/Fiji")
    '19891202011405'

The system does the shift if the date comes with a valid timezone:

    >>> dt = dtime.ansi_to_dt("19891201131405")
    >>> dt = dtime.to_zone(dt, "Pacific/Fiji")
    >>> dtime.to_ansi(dt, timezone="Pacific/Fiji")
    '19891201131405'

    >>> dtime.to_ansi(dt, timezone="Etc/GMT")
    '19891201011405'

If the timezone is not valid, the system returns in ANSI without shifts:

    >>> dtime.to_ansi(dt, timezone="+03")
    '19891201131405'

    >>> dtime.to_ansi(dt, timezone="Mars")
    '19891201131405'


Relative delta between two dates
................................

We can extract the relative delta between two dates:

    >>> dt1 = dtime.ansi_to_dt("20230515104405")
    >>> dt2 = dtime.ansi_to_dt("20230515114405")
    >>> dtime.get_relative_delta(dt1, dt2)
    relativedelta(hours=+1)

We can even compare two dates from two different timezones:

    >>> dt1_cet = dtime.to_zone(dt1, "CET")
    >>> dt2_utc = dtime.to_zone(dt2, "UTC")
    >>> dtime.get_relative_delta(dt1_cet, dt2_utc)
    relativedelta(hours=+3)

    >>> dt1_cet = dtime.to_zone(dt1, "CET")
    >>> dt2_pcf = dtime.to_zone(dt2, "Pacific/Fiji")
    >>> dtime.get_relative_delta(dt1_cet, dt2_pcf)
    relativedelta(hours=-9)

If we compare a naive timezone, system uses the timezone of the other date:

    >>> dt1_cet = dtime.to_zone(dt1, "CET")
    >>> dt2_naive = dt2.replace(tzinfo=None)
    >>> dtime.get_relative_delta(dt1_cet, dt2_naive)
    relativedelta(hours=+3)

It also works when both are timezone naive:

    >>> dt1_naive = dt1.replace(tzinfo=None)
    >>> dt2_naive = dt2.replace(tzinfo=None)
    >>> dtime.get_relative_delta(dt1_naive, dt2_naive)
    relativedelta(hours=+1)

If we don't specify `dt2`, system simply uses current datetime:

    >>> rel_now = dtime.get_relative_delta(dt1, datetime.now())
    >>> rel_wo = dtime.get_relative_delta(dt1)
    >>> rel_now = (rel_now.years, rel_now.months, rel_now.days, rel_now.hours)
    >>> rel_wo = (rel_wo.years, rel_wo.months, rel_wo.days, rel_wo.hours)
    >>> rel_now == rel_wo
    True

We can even compare min and max dates:

    >>> dt1 = dtime.datetime.min
    >>> dt2 = dtime.datetime.max
    >>> dtime.get_relative_delta(dtime.datetime.min, dtime.datetime.max)
    relativedelta(years=+9998, months=+11, days=+30, hours=+23, minutes=+59, seconds=+59, microseconds=+999999)

We can even call the function with types that are not datetime, but can be
converted to datetime:

    >>> dtime.get_relative_delta("19891201131405", "20230515114400")
    relativedelta(years=+33, months=+5, days=+13, hours=+22, minutes=+29, seconds=+55)

But raises a `ValueError` if non-valid dates are used:

    >>> dtime.get_relative_delta("17891301132505")
    Traceback (most recent call last):
    ...
    ValueError: No valid date or dates

Even if the from date is correct, but not the to date:

    >>> dtime.get_relative_delta("19891201131405", "20230535114400")
    Traceback (most recent call last):
    ...
    ValueError: No valid date or dates

We can also compare two datetimes, being the "from" earlier than "to":

    >>> dtime.get_relative_delta("20230515114400", "19891201131405")
    relativedelta(years=-33, months=-5, days=-13, hours=-22, minutes=-29, seconds=-55)

Or compare two dates that are exactly the same:

    >>> dtime.get_relative_delta("20230515114400", "20230515114400")
    relativedelta()

We can compare dates without time as well:

    >>> from_date = dtime.date(2023, 5, 6)
    >>> to_date = dtime.date(2023, 5, 7)
    >>> dtime.get_relative_delta(from_date, to_date)
    relativedelta(days=+1)


Convert timedelta to Dict Object and Back
................................

Let's try to initialize a timedelta object and convert it first:

    >>> from datetime import timedelta
    >>> td = timedelta(days=1, hours=1, minutes=1, seconds=1)
    >>> dict_td = dtime.timedelta_to_dict(td)
    >>> isinstance(dict_td, dict)
    True
    >>> dict_td.get('days')
    1
    >>> dict_td.get('hours')
    1
    >>> dict_td.get('minutes')
    1
    >>> dict_td.get('seconds')
    1

If the wrong type is passed, a TypeError exception will be raised:

    >>> dtime.timedelta_to_dict(str("wrong parameter type"))
    Traceback (most recent call last):
    ...
    TypeError: <type 'str'> is not supported

A default value can be set to be returned in case the passed value has the wrong type:

    >>> dtime.timedelta_to_dict(str("wrong parameter type"), default="DEFAULT IS RETURNED")
    'DEFAULT IS RETURNED'

Convert the object back to timedelta:

    >>> td_dict_td = dtime.to_timedelta(dict_td)
    >>> td_dict_td
    datetime.timedelta(1, 3661)
    >>> isinstance(td_dict_td, timedelta)
    True
    >>> td_dict_td == td
    True

Passing the wrong type raises a TypeError exception:

    >>> dtime.to_timedelta(str("wrong parameter type"))
    Traceback (most recent call last):
    ...
    TypeError: <type 'str'> is not supported

A default value can be set to be returned in case the passed value has the wrong type:

    >>> dtime.to_timedelta(str("wrong parameter type"), default="DEFAULT IS RETURNED")
    'DEFAULT IS RETURNED'

Dict keys except: ['days', 'hours', 'minutes', 'seconds'] are just ignored:

    >>> dtime.to_timedelta({'love': True, 'days': 1})
    datetime.timedelta(1)

Wrong values are ignored and replaced with 0:

    >>> dtime.to_timedelta({'days': 'wrong value'})
    datetime.timedelta(0)
