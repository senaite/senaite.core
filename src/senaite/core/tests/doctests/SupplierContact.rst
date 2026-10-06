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
    >>> from bika.lims.content.suppliercontact import SupplierContact \
    ...     as ATSupplierContact
    >>> from bika.lims.interfaces import IDeactivable
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from senaite.core.interfaces import ISupplierContact
    >>> from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
    >>> from senaite.core.upgrade.v02_07_000 import \
    ...     migrate_suppliercontact_to_dx

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


Migration of an Archetypes supplier contact
...........................................

This PR removes the Archetypes factory, so an existing instance is simulated
by instantiating the old class directly:

    >>> at_contact = ATSupplierContact("at-contact")
    >>> ignored = supplier._setObject("at-contact", at_contact)
    >>> at_contact = supplier["at-contact"]
    >>> at_contact.initializeArchetype()
    >>> at_contact.setFirstname("John")
    >>> at_contact.setSurname("Smith")
    >>> at_contact.setEmailAddress("john@example.com")
    >>> at_contact.setJobTitle("Purchasing")

    >>> api.is_at_content(at_contact)
    True

    >>> at_uid = api.get_uid(at_contact)

Migrate it:

    >>> migrate_suppliercontact_to_dx(at_contact)

The object is Dexterity now and kept its UID, so every reference to it keeps
resolving:

    >>> migrated = api.get_object_by_uid(at_uid)
    >>> api.is_dexterity_content(migrated)
    True

    >>> api.get_uid(migrated) == at_uid
    True

The values were carried over:

    >>> migrated.getFullname()
    'John Smith'

    >>> migrated.getEmailAddress()
    'john@example.com'

    >>> migrated.getJobTitle()
    'Purchasing'

And it lives in the same supplier, under the original ID:

    >>> api.get_parent(migrated) == supplier
    True

    >>> api.get_id(migrated)
    'at-contact'
