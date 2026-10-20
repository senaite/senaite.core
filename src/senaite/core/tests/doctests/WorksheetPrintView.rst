Worksheet print view
--------------------

The print view of a worksheet resolves the signature of the lab contact that
is linked to the user printing it.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t WorksheetPrintView


Test Setup
..........

Needed Imports:

    >>> import base64

    >>> from bika.lims import api
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from senaite.core.browser.worksheets.worksheet.printview import \
    ...     PrintView

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup

Grant the required privileges:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Manager"])

A 1x1 pixel PNG we can use as a signature:

    >>> SIGNATURE = base64.b64decode(
    ...     "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8"
    ...     "z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")


Signature of the user that prints the worksheet
...............................................

Create a worksheet and the print view for it:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> view = PrintView(worksheet, request)

Without a lab contact linked to the current user, there is no signature:

    >>> data = view._printedby_data(worksheet)
    >>> data.get("signature")

Create a lab contact, link it to the current user and give it a signature:

    >>> contact = api.create(setup.bika_labcontacts, "LabContact",
    ...                      Firstname="Lab", Lastname="Manager")
    >>> contact.setUsername(TEST_USER_ID)
    >>> contact.getField("Signature").set(contact, SIGNATURE,
    ...                                   filename="signature.png")
    >>> contact.reindexObject()

Note lab contacts are indexed in the contact catalog and not in the setup
catalog, so the lookup has to be done there:

    >>> api.get_catalogs_for(contact)
    [<ContactCatalog at /plone/senaite_catalog_contact>]

The print view resolves the signature now:

    >>> data = view._printedby_data(worksheet)
    >>> signature = data.get("signature")
    >>> signature is not None
    True

The url points to the `Signature` field of the contact, and the name of the
field is not repeated, cause the url of the image contains it already:

    >>> signature == "{}/Signature".format(api.get_url(contact))
    True
