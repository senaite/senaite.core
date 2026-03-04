Contacts
--------

Tests catalog indexing behavior for contact types in the contact catalog.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t Contacts


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from Products.CMFCore.indexing import processQueue
    >>> from senaite.core.catalog import CONTACT_CATALOG

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])


Contact Catalog Indexing
........................

Create a global Contact in the setup contacts folder:

    >>> contact = api.create(
    ...     setup.contacts,
    ...     "Contact",
    ...     Firstname="Rita",
    ...     Surname="Mohale",
    ...     EmailAddress="rita@lab.test",
    ... )
    >>> processing = processQueue()

The Contact should be indexed in the contact catalog:

    >>> brains = api.search({"UID": api.get_uid(contact)}, CONTACT_CATALOG)
    >>> len(brains)
    1

The `getFullname` index should return the contact's full name:

    >>> brains = api.search(
    ...     {"portal_type": "Contact", "getFullname": "Rita Mohale"},
    ...     CONTACT_CATALOG,
    ... )
    >>> len(brains)
    1

The `sortable_title` index should allow sorting by full name:

    >>> brains = api.search(
    ...     {
    ...         "portal_type": "Contact",
    ...         "UID": api.get_uid(contact),
    ...         "sort_on": "sortable_title",
    ...     },
    ...     CONTACT_CATALOG,
    ... )
    >>> len(brains)
    1


LabContact Catalog Indexing
...........................

The `listing_searchable_text` adapter must be registered for `ILabContact`
so that text search returns results for lab contacts.

Create a LabContact with known attributes:

    >>> labcontact = api.create(
    ...     bikasetup.bika_labcontacts,
    ...     "LabContact",
    ...     Firstname="William",
    ...     Surname="Testperson",
    ...     EmailAddress="william@lab.test",
    ... )
    >>> processing = processQueue()

The LabContact should be indexed in the contact catalog:

    >>> brains = api.search({"UID": api.get_uid(labcontact)}, CONTACT_CATALOG)
    >>> len(brains)
    1

Searching by `listing_searchable_text` should find the LabContact by first name:

    >>> brains = api.search(
    ...     {
    ...         "portal_type": "LabContact",
    ...         "listing_searchable_text": "William",
    ...     },
    ...     CONTACT_CATALOG,
    ... )
    >>> len(brains)
    1

Searching by last name should also return the LabContact:

    >>> brains = api.search(
    ...     {
    ...         "portal_type": "LabContact",
    ...         "listing_searchable_text": "Testperson",
    ...     },
    ...     CONTACT_CATALOG,
    ... )
    >>> len(brains)
    1

The `sortable_title` index should allow ordering results by full name:

    >>> brains = api.search(
    ...     {
    ...         "portal_type": "LabContact",
    ...         "UID": api.get_uid(labcontact),
    ...         "sort_on": "sortable_title",
    ...     },
    ...     CONTACT_CATALOG,
    ... )
    >>> len(brains)
    1
