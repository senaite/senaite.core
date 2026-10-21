Supplier Contact Migration
--------------------------

Migration of an Archetypes supplier contact to Dexterity. This test goes
together with the Archetypes class `bika.lims.content.suppliercontact`, so
remove it when that class is removed.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t SupplierContactMigration


Test Setup
..........

Needed Imports:

    >>> import transaction

    >>> from bika.lims import api
    >>> from bika.lims.content.suppliercontact import SupplierContact \
    ...     as ATSupplierContact
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from senaite.core.upgrade.v02_07_000 import \
    ...     migrate_suppliercontact_to_dx

Variables:

    >>> portal = self.portal
    >>> setup = api.get_senaite_setup()
    >>> catalog = api.get_tool("senaite_catalog_contact")

Grant the required privileges:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Manager"])
    >>> transaction.commit()

A supplier to hold the contacts:

    >>> supplier = api.create(setup.suppliers, "Supplier", Name="Acme")


Migrate an Archetypes supplier contact
......................................

The Archetypes type is no longer registered, so an existing contact is
simulated by instantiating the old class directly:

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

It is indexed with the contact indexers of the new type:

    >>> catalog.getIndexDataForUID(api.get_path(migrated))["sortable_title"]
    'john smith'
