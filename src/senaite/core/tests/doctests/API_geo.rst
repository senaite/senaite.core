SENAITE geo API
---------------

The geo API provides functions for search and manipulation of geographic
entities/locations, like countries and subdivisions.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t API_geo

Test Setup
..........

Imports

    >>> from senaite.core.api import geo


Get all countries
.................

    >>> countries = geo.get_countries()
    >>> len(countries)
    249

Check if an object is a country
...............................

    >>> geo.is_country(countries[0])
    True

    >>> geo.is_country("Spain")
    False


Get a country by term
.....................

    >>> geo.get_country("es")
    Country(alpha_2=u'ES', alpha_3=u'ESP', name=u'Spain', numeric=u'724', official_name=u'Kingdom of Spain')

    >>> geo.get_country("Spain")
    Country(alpha_2=u'ES', alpha_3=u'ESP', name=u'Spain', numeric=u'724', official_name=u'Kingdom of Spain')

    >>> geo.get_country("Kingdom of Spain")
    Country(alpha_2=u'ES', alpha_3=u'ESP', name=u'Spain', numeric=u'724', official_name=u'Kingdom of Spain')


Get a non-existing country
..........................

    >>> geo.get_country("Pluto")
    Traceback (most recent call last):
    [...]
    ValueError: Could not find a record for 'pluto'

    >>> geo.get_country("Pluto", default=None) is None
    True


Get a subdivision or country
............................

We can directly retrieve a subdivision or a country in a single call:

    >>> geo.get_country_or_subdivision("Spain")
    Country(alpha_2=u'ES', alpha_3=u'ESP', name=u'Spain', numeric=u'724', official_name=u'Kingdom of Spain')

    >>> geo.get_country_or_subdivision("Catalunya")
    Subdivision(code=u'ES-CT', country_code=u'ES', name=u'Catalunya', parent_code=None, type=u'Autonomous community')

    >>> geo.get_country_or_subdivision("Pluto")
    Traceback (most recent call last):
    [...]
    ValueError: Could not find a record for 'pluto'


Get subdivisions of a country
.............................

We can get the subdivisions immediately below a Country object, sorted by code:

    >>> country = geo.get_country("es")
    >>> subdivisions = geo.get_subdivisions(country)
    >>> subdivisions[0]
    Subdivision(code=u'ES-AN', country_code=u'ES', name=u'Andaluc\xeda', parent_code=None, type=u'Autonomous community')

    >>> len(subdivisions)
    19

Or we can directluy get them with any search term for country:

    >>> subdivisions = geo.get_subdivisions("es")
    >>> subdivisions[0]
    Subdivision(code=u'ES-AN', country_code=u'ES', name=u'Andaluc\xeda', parent_code=None, type=u'Autonomous community')

    >>> len(subdivisions)
    19

Check if an object is a Subdivision
...................................

    >>> geo.is_subdivision(subdivisions[0])
    True

    >>> geo.is_subdivision(country)
    False

    >>> geo.is_subdivision("Catalunya")
    False

    >>> geo.is_country(subdivisions[0])
    False


Get subdivisions of a subdivision
.................................

Likewise, we can get the subdivisions immediately below a Subdivision object,
sorted by code:

    >>> subdivisions = geo.get_subdivisions("es")
    >>> subsubdivisions = geo.get_subdivisions(subdivisions[0])
    >>> subsubdivisions[0]
    Subdivision(code=u'ES-AL', country_code=u'ES', name=u'Almer\xeda', parent=u'AN', parent_code=u'ES-AN', type=u'Province')

    >>> len(subsubdivisions)
    8


Get the code of a country
.........................

We can obtain the 2-letter code of a country directly:

    >>> geo.get_country_code(country)
    u'ES'

Or from any of its subdivisions:

    >>> geo.get_country_code(subdivisions[0])
    u'ES'

    >>> geo.get_country_code(subsubdivisions[0])
    u'ES'

We can even get the country code with only text:

    >>> geo.get_country_code("Spain")
    u'ES'

    >>> geo.get_country_code("Germany")
    u'DE'


Get a subdivision
.................

Is also possible to retrieve a subdivision by search term directly:

    >>> geo.get_subdivision("ES-CA")
    Subdivision(code=u'ES-CA', country_code=u'ES', name=u'C\xe1diz', parent=u'AN', parent_code=u'ES-AN', type=u'Province')

    >>> geo.get_subdivision("Catalunya")
    Subdivision(code=u'ES-CT', country_code=u'ES', name=u'Catalunya', parent_code=None, type=u'Autonomous community')

    >>> geo.get_subdivision("Washington")
    Subdivision(code=u'US-WA', country_code=u'US', name=u'Washington', parent_code=None, type=u'State')

    >>> geo.get_subdivision("Barcelona")
    Subdivision(code=u'ES-B', country_code=u'ES', name=u'Barcelona', parent=u'CT', parent_code=u'ES-CT', type=u'Province')

We can also specify the parent:

    >>> spain = geo.get_country("es")
    >>> catalunya = geo.get_subdivision("Catalunya", parent=spain)
    >>> catalunya
    Subdivision(code=u'ES-CT', country_code=u'ES', name=u'Catalunya', parent_code=None, type=u'Autonomous community')

So only subdivisions immediately below the specified parent are returned:

    >>> geo.get_subdivision("Barcelona", parent=spain, default=None) is None
    True

    >>> geo.get_subdivision("Barcelona", parent=catalunya)
    Subdivision(code=u'ES-B', country_code=u'ES', name=u'Barcelona', parent=u'CT', parent_code=u'ES-CT', type=u'Province')

We can even specify a search term for the parent:

    >>> geo.get_subdivision("Barcelona", parent="Catalunya")
    Subdivision(code=u'ES-B', country_code=u'ES', name=u'Barcelona', parent=u'CT', parent_code=u'ES-CT', type=u'Province')


Converting geographical coordinate in DD to DMS
...............................................

Is possible to convert a geographical coordinate in decimal degrees (DD) to
a dict with degrees, minutes and seconds (DMS):

    >>> latitude = 41.483504
    >>> dms = geo.to_dms(latitude)
    >>> keys = sorted(dms.keys())
    >>> keys
    ['degrees', 'minutes', 'seconds']

    >>> [dms.get(key) for key in keys]
    [41, 29, 0.6144]

We can also decrease the number of decimals of seconds by means of precision:

    >>> dms = geo.to_dms(latitude, precision=2)
    >>> [dms.get(key) for key in sorted(dms.keys())]
    [41, 29, 0.61]

If the value passed in is not floatable, the system rises an error:

    >>> geo.to_dms("yummi")
    Traceback (most recent call last):
    ...
    ValueError: Expected decimal degrees to be a floatable, but got 'yummi'

We can use a default value as a fallback though:

    >>> geo.to_dms("yummi", default=None) is None
    True

The system rises an error if the precision is not valid:

    >>> geo.to_dms(latitude, precision=None)
    Traceback (most recent call last):
    ...
    TypeError: Expected precision to be an `int`, but got <type 'NoneType'>

Even if we use a default as a fallback:

    >>> geo.to_dms(latitude, precision=None, default=None)
    Traceback (most recent call last):
    ...
    TypeError: Expected precision to be an `int`, but got <type 'NoneType'>


Converting latitude coordinate in DD to DMS
...........................................

If we know the coordinate is a latitude, we can use a specific function that
besides the conversion from DMS to DD, it will also take the bearing into
account and check the degrees are within range.

    >>> latitude = 41.483504
    >>> dms = geo.to_latitude_dms(latitude)
    >>> keys = sorted(dms.keys())
    >>> keys
    ['bearing', 'degrees', 'minutes', 'seconds']

    >>> [dms.get(key) for key in keys]
    ['N', 41, 29, 0.6144]

System handles North and South as +/-:

    >>> dms = geo.to_latitude_dms(-latitude)
    >>> [dms.get(key) for key in keys]
    ['S', 41, 29, 0.6144]

The system rises an error if the latitude is out of range:

    >>> geo.to_latitude_dms(90.0000001)
    Traceback (most recent call last):
    ...
    ValueError: Latitude must be within -90 and 90 degrees

    >>> geo.to_latitude_dms(-90.0000001)
    Traceback (most recent call last):
    ...
    ValueError: Latitude must be within -90 and 90 degrees

Converting longitude coordinate in DD to DMS
............................................

If we know the coordinate is a longitude, we can use a specific function that
besides the conversion from DMS to DD, it will also take the bearing into
account and check the degrees are within range.

    >>> longitude = 2.051877
    >>> dms = geo.to_longitude_dms(longitude)
    >>> keys = sorted(dms.keys())
    >>> keys
    ['bearing', 'degrees', 'minutes', 'seconds']

    >>> [dms.get(key) for key in keys]
    ['E', 2, 3, 6.7572]

System handles East and West as +/-:

    >>> dms = geo.to_longitude_dms(-longitude)
    >>> [dms.get(key) for key in keys]
    ['W', 2, 3, 6.7572]

The system rises an error if the longitude is out of range:

    >>> geo.to_longitude_dms(180.0000001)
    Traceback (most recent call last):
    ...
    ValueError: Longitude must be within -180 and 180 degrees

    >>> geo.to_longitude_dms(-180.0000001)
    Traceback (most recent call last):
    ...
    ValueError: Longitude must be within -180 and 180 degrees


Converting geographical coordinate in DMS to DD
...............................................

Is possible to convert a geographical coordinate as dict with degrees, minutes
and seconds (DMS) to decimal degrees (DD):

    >>> dms = {"degrees": 41, "minutes": 29, "seconds": 0.6144}
    >>> geo.to_decimal_degrees(dms)
    41.483504

We can also decrease the number of decimals by means of precision:

    >>> geo.to_decimal_degrees(dms, precision=2)
    41.48

If the value passed in is not from the valid type, the system rises an error:

    >>> geo.to_decimal_degrees("yummi")
    Traceback (most recent call last):
    ...
    TypeError: Expected dms to be a dict, but got 'yummi'

We can use a default value as a fallback though:

    >>> geo.to_decimal_degrees("yummi", default=None) is None
    True

The system rises an error if the precision is not valid:

    >>> geo.to_decimal_degrees(dms, precision=None)
    Traceback (most recent call last):
    ...
    TypeError: Expected precision to be an `int`, but got <type 'NoneType'>

Even if we use a default as a fallback:

    >>> geo.to_decimal_degrees(dms, precision=None, default=None)
    Traceback (most recent call last):
    ...
    TypeError: Expected precision to be an `int`, but got <type 'NoneType'>

It also handles bearing properly:

    >>> dms = {"degrees": 41, "minutes": 29, "seconds": 0.6144, "bearing": "S"}
    >>> geo.to_decimal_degrees(dms)
    -41.483504

It also handles bearing properly:

    >>> dms = {"degrees": 2, "minutes": 3, "seconds": 6.7572, "bearing": "W"}
    >>> geo.to_decimal_degrees(dms)
    -2.051877
