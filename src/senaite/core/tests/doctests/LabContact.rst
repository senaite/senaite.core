LabContact
----------

Tests that the `listing_searchable_text`, `sortable_title`, and `getParentUID`
indexes are correctly populated for `LabContact` and `SupplierContact` objects
in the contact catalog.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t LabContact


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
    >>> bikasetup = portal.bika_setup

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])


LabContact listing_searchable_text Indexing
...........................................

Create a LabContact with known attributes:

    >>> labcontact = api.create(
    ...     bikasetup.bika_labcontacts,
    ...     "LabContact",
    ...     Firstname="William",
    ...     Lastname="Testperson",
    ...     EmailAddress="william@lab.test",
    ... )

Process the indexing queue to ensure the object is cataloged:

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


LabContact sortable_title Indexing
...................................

The `sortable_title` index should be populated and allow sorting by full name.
Query with a sort to verify the index is present:

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


LabContact getParentUID Indexing
.................................

LabContacts are not inside a client, so `getParentUID` should return an empty
string:

    >>> brains = api.search({"UID": api.get_uid(labcontact)}, CONTACT_CATALOG)
    >>> brain = brains[0]
    >>> brain.getParentUID
    ''


SupplierContact listing_searchable_text Indexing
................................................

Create a Supplier and a SupplierContact:

    >>> supplier = api.create(
    ...     bikasetup.bika_suppliers,
    ...     "Supplier",
    ...     Name="Test Supplier",
    ... )
    >>> suppliercontact = api.create(
    ...     supplier,
    ...     "SupplierContact",
    ...     Firstname="Jane",
    ...     Lastname="Tester",
    ...     EmailAddress="jane@supplier.test",
    ... )

Process the indexing queue:

    >>> processing = processQueue()

The SupplierContact should be indexed in the contact catalog:

    >>> brains = api.search(
    ...     {"UID": api.get_uid(suppliercontact)}, CONTACT_CATALOG
    ... )
    >>> len(brains)
    1

Searching by `listing_searchable_text` should find the SupplierContact:

    >>> brains = api.search(
    ...     {
    ...         "portal_type": "SupplierContact",
    ...         "listing_searchable_text": "Jane",
    ...     },
    ...     CONTACT_CATALOG,
    ... )
    >>> len(brains)
    1

Searching by last name should also return the SupplierContact:

    >>> brains = api.search(
    ...     {
    ...         "portal_type": "SupplierContact",
    ...         "listing_searchable_text": "Tester",
    ...     },
    ...     CONTACT_CATALOG,
    ... )
    >>> len(brains)
    1
