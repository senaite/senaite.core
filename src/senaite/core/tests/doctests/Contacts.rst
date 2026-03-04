Contacts
--------

Tests catalog indexing behavior for all contact types: `Contact`,
`LabContact`, and `SupplierContact`.

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
    ...     Lastname="Mohale",
    ...     EmailAddress="rita@lab.test",
    ... )
    >>> processing = processQueue()

The Contact should be indexed in the contact catalog:

    >>> brains = api.search({"UID": api.get_uid(contact)}, CONTACT_CATALOG)
    >>> len(brains)
    1

Searching by `listing_searchable_text` should find the Contact by first name:

    >>> brains = api.search(
    ...     {
    ...         "portal_type": "Contact",
    ...         "listing_searchable_text": "Rita",
    ...     },
    ...     CONTACT_CATALOG,
    ... )
    >>> len(brains)
    1

Searching by last name should also return the Contact:

    >>> brains = api.search(
    ...     {
    ...         "portal_type": "Contact",
    ...         "listing_searchable_text": "Mohale",
    ...     },
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

Create a LabContact with known attributes:

    >>> labcontact = api.create(
    ...     bikasetup.bika_labcontacts,
    ...     "LabContact",
    ...     Firstname="William",
    ...     Lastname="Testperson",
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

The `sortable_title` index should be populated and allow sorting by full name:

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

LabContacts are not inside a client, so `getParentUID` should be empty:

    >>> brain = api.search({"UID": api.get_uid(labcontact)}, CONTACT_CATALOG)[0]
    >>> brain.getParentUID
    ''


SupplierContact Catalog Indexing
.................................

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
    >>> processing = processQueue()

The SupplierContact should be indexed in the contact catalog:

    >>> brains = api.search(
    ...     {"UID": api.get_uid(suppliercontact)}, CONTACT_CATALOG
    ... )
    >>> len(brains)
    1

Searching by `listing_searchable_text` should find the SupplierContact by first name:

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
