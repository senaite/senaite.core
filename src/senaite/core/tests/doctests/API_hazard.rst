SENAITE hazard API
------------------

The ``senaite.core.api.hazard`` module exposes helpers for resolving
hazard pictograms (GHS + ISO 7010) for samples, reference objects and
sample types, and a small renderer that the listings use to keep the
``<img>`` markup consistent across call sites.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t API_hazard


Test Setup
..........

    >>> from senaite.core.api import hazard as hazard_api


Hazard pictogram URL for a known code
.....................................

    >>> hazard_api.get_pictogram_url("GHS01").endswith(
    ...     "/++plone++senaite.core.static/images/ghs/GHS01.svg")
    True

    >>> hazard_api.get_pictogram_url("GHS06").endswith(
    ...     "/++plone++senaite.core.static/images/ghs/GHS06.svg")
    True


Hazard pictogram URL for an unknown code
........................................

Returns an empty string instead of raising:

    >>> hazard_api.get_pictogram_url("GHSXX")
    u''

    >>> hazard_api.get_pictogram_url("")
    u''

    >>> hazard_api.get_pictogram_url(None)
    u''


ISO 7010 W001 fallback pictogram URL
....................................

Used as the generic warning when a sample is hazardous but no
hazard category has been assigned.

    >>> hazard_api.get_warning_pictogram_url().endswith(
    ...     "/++plone++senaite.core.static/images/iso/W001.svg")
    True


View-model dict for a single hazard category
............................................

    >>> picto = hazard_api.get_pictogram("GHS06")
    >>> picto["code"]
    'GHS06'

    >>> picto["url"].endswith("/images/ghs/GHS06.svg")
    True

The ``alt`` and ``title`` carry the translated label so screen
readers announce the hazard meaning instead of the opaque code:

    >>> picto["title"].startswith("GHS06")
    True

    >>> picto["alt"] == picto["title"]
    True

Unknown codes return ``None`` instead of a placeholder dict:

    >>> hazard_api.get_pictogram("GHSXX") is None
    True


Pictograms for a list of codes
..............................

When ``hazardous`` is false, no pictogram is returned regardless of
the codes:

    >>> hazard_api.get_pictograms_for_codes(["GHS01"], hazardous=False)
    []

When the sample is hazardous but the code list is empty, the W001
fallback is returned:

    >>> result = hazard_api.get_pictograms_for_codes([], hazardous=True)
    >>> len(result)
    1

    >>> result[0]["code"]
    ''

    >>> result[0]["url"].endswith("/images/iso/W001.svg")
    True

A ``None`` code list is treated as empty:

    >>> result = hazard_api.get_pictograms_for_codes(None, hazardous=True)
    >>> len(result)
    1

    >>> result[0]["code"]
    ''

Unknown codes are silently skipped, known codes are kept in order:

    >>> result = hazard_api.get_pictograms_for_codes(
    ...     ["GHS01", "GHSXX", "GHS06"], hazardous=True)
    >>> [p["code"] for p in result]
    ['GHS01', 'GHS06']


Pictograms for a reference object
.................................

``get_pictograms_for_reference`` accepts any object (or brain) that
carries ``getHazardous`` and ``getHazardCategories`` accessors:

    >>> class Ref(object):
    ...     def __init__(self, hazardous, categories):
    ...         self._hazardous = hazardous
    ...         self._categories = categories
    ...     def getHazardous(self):
    ...         return self._hazardous
    ...     def getHazardCategories(self):
    ...         return self._categories

A non-hazardous object yields no pictograms regardless of categories:

    >>> hazard_api.get_pictograms_for_reference(Ref(False, ["GHS01"]))
    []

Hazardous + empty categories falls back to the W001 warning:

    >>> result = hazard_api.get_pictograms_for_reference(Ref(True, []))
    >>> len(result)
    1

    >>> result[0]["url"].endswith("/images/iso/W001.svg")
    True

Hazardous + categories returns one pictogram per known code:

    >>> result = hazard_api.get_pictograms_for_reference(
    ...     Ref(True, ["GHS01", "GHS06"]))
    >>> [p["code"] for p in result]
    ['GHS01', 'GHS06']


Rendering a pictogram view-model as HTML
........................................

``render_pictogram_img`` centralizes the listing markup so the four
listing call sites stay consistent on attributes and escaping:

    >>> picto = hazard_api.get_pictogram("GHS01")
    >>> html = hazard_api.render_pictogram_img(picto)
    >>> isinstance(html, bytes)
    True

    >>> b'src="' in html and b'GHS01.svg' in html
    True

    >>> b'class="hazard-pictogram-mini"' in html
    True

The CSS class can be overridden by the caller:

    >>> b'class="big"' in hazard_api.render_pictogram_img(picto, "big")
    True
