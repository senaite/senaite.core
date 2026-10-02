Organization
------------

Tests for the DX `Organization` base type, which is the shared parent of
`Supplier`, `Manufacturer`, and `Laboratory`. Every field carried by the
type has to accept non-ASCII values transparently: an umlaut in a city
name, a Cyrillic supplier title, or a full-width country code must
survive a round trip through the getters, setters, and every composed
accessor without an implicit ASCII encode.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t OrganizationPrintAddress


Test Setup
..........

Needed imports:

    >>> from bika.lims import api
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.schema.addressfield import BILLING_ADDRESS
    >>> from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
    >>> from senaite.core.schema.addressfield import POSTAL_ADDRESS

Variables:

    >>> portal = self.portal
    >>> setup = api.get_senaite_setup()
    >>> suppliers = setup.suppliers
    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])


Create a Supplier with a non-ASCII title
........................................

Titles carry the organisation name and end up in listings, notifications,
and printed reports. They must accept unicode with combining marks and
non-Latin scripts:

    >>> supplier = api.create(suppliers, "Supplier")
    >>> supplier.setName(u"M\xfcller Labor")

`getName` is a BBB accessor for the AT contract and returns a UTF-8
encoded byte string:

    >>> supplier.getName()
    'M\xc3\xbcller Labor'


Round-trip the three address slots
..................................

An `Organization` carries a Postal, a Physical, and a Billing address, all
sharing the same schema. The setters accept unicode and the getters return
it unchanged:

    >>> postal = {
    ...     "address": u"Beispielstra\xdfe 1",
    ...     "city": u"M\xfclheim",
    ...     "zip": u"10000",
    ...     "state": u"",
    ...     "country": u"Testland",
    ... }
    >>> physical = {
    ...     "address": u"Am H\xfcgel 2",
    ...     "city": u"Sch\xf6nfeld",
    ...     "zip": u"20000",
    ...     "state": u"",
    ...     "country": u"Testland",
    ... }
    >>> billing = {
    ...     "address": u"Postfach 3",
    ...     "city": u"Gr\xfcnstadt",
    ...     "zip": u"30000",
    ...     "state": u"S\xfcdregion",
    ...     "country": u"Testland",
    ... }

The address field is a single list of typed entries. Seed one entry per
slot, then use the per-slot setters to fill them:

    >>> supplier.setAddress([
    ...     {"type": POSTAL_ADDRESS},
    ...     {"type": PHYSICAL_ADDRESS},
    ...     {"type": BILLING_ADDRESS},
    ... ])
    >>> supplier.setPostalAddress(postal)
    >>> supplier.setPhysicalAddress(physical)
    >>> supplier.setBillingAddress(billing)

Each getter returns exactly what went in:

    >>> supplier.getPostalAddress()["city"]
    u'M\xfclheim'
    >>> supplier.getPhysicalAddress()["city"]
    u'Sch\xf6nfeld'
    >>> supplier.getBillingAddress()["city"]
    u'Gr\xfcnstadt'


getPrintAddress composes the three lines
........................................

`getPrintAddress` picks the first non-empty address (Postal wins over
Physical wins over Billing) and returns three unicode lines: street,
`<city> <zip>`, and `<state> <country>`. Any implicit ASCII encode along
the way would raise `UnicodeEncodeError` given the umlauts above:

    >>> supplier.getPrintAddress()
    [u'Beispielstra\xdfe 1', u'M\xfclheim 10000', u'Testland']

Each returned line is unicode, so callers that concatenate them into an
email body or a PDF do not have to guess the encoding:

    >>> all(isinstance(line, unicode) for line in supplier.getPrintAddress())
    True

Blank fields collapse cleanly (no stray whitespace, no `None`):

    >>> supplier.setPostalAddress({
    ...     "address": u"", "city": u"M\xfclheim", "zip": u"",
    ...     "state": u"", "country": u""})
    >>> supplier.getPrintAddress()
    [u'', u'M\xfclheim', u'']


Fallback to Physical when Postal is empty
.........................................

When the Postal slot has no `city`, `getPrintAddress` falls back to the
Physical address, and then to Billing. The fallback path must handle
non-ASCII fields the same way:

    >>> supplier.setPostalAddress({
    ...     "address": u"", "city": u"", "zip": u"",
    ...     "state": u"", "country": u""})
    >>> supplier.getPrintAddress()
    [u'Am H\xfcgel 2', u'Sch\xf6nfeld 20000', u'Testland']

    >>> supplier.setPhysicalAddress({
    ...     "address": u"", "city": u"", "zip": u"",
    ...     "state": u"", "country": u""})
    >>> supplier.getPrintAddress()
    [u'Postfach 3', u'Gr\xfcnstadt 30000', u'S\xfcdregion Testland']

An Organization with no populated address at all returns an empty list
rather than a list of blank strings:

    >>> supplier.setBillingAddress({
    ...     "address": u"", "city": u"", "zip": u"",
    ...     "state": u"", "country": u""})
    >>> supplier.getPrintAddress()
    []
