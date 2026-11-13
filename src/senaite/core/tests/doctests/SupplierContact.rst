Supplier Contact
----------------

Supplier contacts are the people of a supplier we deal with. The type adds no
fields of its own, the schema of `Person` is the whole contract.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t SupplierContact


Test Setup
..........

Needed Imports:

    >>> import transaction

    >>> from bika.lims import api
    >>> from bika.lims.interfaces import IDeactivable
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from senaite.core.interfaces import ISupplierContact
    >>> from senaite.core.schema.addressfield import PHYSICAL_ADDRESS

Variables:

    >>> portal = self.portal
    >>> setup = api.get_senaite_setup()

Grant the required privileges:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Manager"])
    >>> transaction.commit()

A supplier to hold the contacts:

    >>> supplier = api.create(setup.suppliers, "Supplier", Name="Acme")


Create a supplier contact
.........................

    >>> contact = api.create(supplier, "SupplierContact",
    ...                      Firstname="Jane", Surname="Doe")

    >>> api.get_portal_type(contact)
    'SupplierContact'

It is a Dexterity content that provides the marker interface:

    >>> api.is_dexterity_content(contact)
    True

    >>> ISupplierContact.providedBy(contact)
    True

It can be deactivated:

    >>> IDeactivable.providedBy(contact)
    True

The title is calculated from the fullname:

    >>> contact.getFullname()
    'Jane Doe'

    >>> api.get_title(contact)
    'Jane Doe'

It is indexed in the contact catalog, and not in the setup catalog:

    >>> api.get_catalogs_for(contact)
    [<ContactCatalog at /plone/senaite_catalog_contact>]

The contact indexers apply, so the contact can be searched and sorted in the
listing of the supplier:

    >>> catalog = api.get_tool("senaite_catalog_contact")
    >>> results = catalog(portal_type="SupplierContact",
    ...                   listing_searchable_text="jane")
    >>> [api.get_object(brain) for brain in results] == [contact]
    True

    >>> catalog.getIndexDataForUID(api.get_path(contact))["sortable_title"]
    'jane doe'


The fields of Person are available
..................................

    >>> contact.setEmailAddress("jane@example.com")
    >>> contact.getEmailAddress()
    'jane@example.com'

    >>> contact.setJobTitle("Sales")
    >>> contact.getJobTitle()
    'Sales'

    >>> contact.setBusinessPhone("123456")
    >>> contact.getBusinessPhone()
    '123456'

Addresses are stored as records, each one tagged with its type:

    >>> contact.setPhysicalAddress({
    ...     "type": PHYSICAL_ADDRESS, "country": "Germany", "city": "Munich"})
    >>> contact.getPhysicalAddress()["city"]
    'Munich'
