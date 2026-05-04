SENAITE core API
----------------

The senaite.core.api module is the gradual replacement for the
long-standing bika.lims.api. It exposes general-purpose helpers
that do not depend on bika.lims.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t API_core


Test Setup
..........

Imports

    >>> from senaite.core import api


Portal helpers
..............

Get the portal object:

    >>> portal = api.get_portal()
    >>> portal == self.portal
    True

Get the absolute URL of the portal:

    >>> url = api.get_portal_url()
    >>> url == self.portal.absolute_url()
    True

    >>> url.startswith("http")
    True


GHS pictogram URL for a known code
..................................

    >>> api.get_pictogram_url("GHS01").endswith(
    ...     "/++plone++senaite.core.static/images/ghs/GHS01.svg")
    True

    >>> api.get_pictogram_url("GHS06").endswith(
    ...     "/++plone++senaite.core.static/images/ghs/GHS06.svg")
    True


GHS pictogram URL for an unknown code
.....................................

Returns an empty string instead of raising:

    >>> api.get_pictogram_url("GHSXX")
    u''

    >>> api.get_pictogram_url("")
    u''

    >>> api.get_pictogram_url(None)
    u''


ISO 7010 W001 fallback pictogram URL
....................................

Used as the generic warning when a sample is hazardous but no GHS
category has been assigned.

    >>> api.get_warning_pictogram_url().endswith(
    ...     "/++plone++senaite.core.static/images/iso/W001.svg")
    True


View-model dict for a single GHS category
.........................................

    >>> picto = api.get_pictogram("GHS06")
    >>> picto["code"]
    'GHS06'

    >>> picto["alt"]
    'GHS06'

    >>> picto["url"].endswith("/images/ghs/GHS06.svg")
    True

    >>> picto["title"].startswith("GHS06")
    True

Unknown codes return ``None`` instead of a placeholder dict:

    >>> api.get_pictogram("GHSXX") is None
    True


Pictograms for a list of codes
..............................

When ``hazardous`` is false, no pictogram is returned regardless of
the codes:

    >>> api.get_pictograms_for_codes(["GHS01"], hazardous=False)
    []

When the sample is hazardous but the code list is empty, the W001
fallback is returned:

    >>> result = api.get_pictograms_for_codes([], hazardous=True)
    >>> len(result)
    1

    >>> result[0]["code"] is None
    True

    >>> result[0]["url"].endswith("/images/iso/W001.svg")
    True

A ``None`` code list is treated as empty:

    >>> result = api.get_pictograms_for_codes(None, hazardous=True)
    >>> len(result)
    1

    >>> result[0]["code"] is None
    True

Unknown codes are silently skipped, known codes are kept in order:

    >>> result = api.get_pictograms_for_codes(
    ...     ["GHS01", "GHSXX", "GHS06"], hazardous=True)
    >>> [p["code"] for p in result]
    ['GHS01', 'GHS06']
