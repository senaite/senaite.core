Global Contacts
---------------

SENAITE allows contacts to be created globally in the setup folder as well as
under specific clients. Global contacts can be used across multiple clients.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t GlobalContacts

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.interfaces import IClient
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from senaite.core.catalog import CONTACT_CATALOG

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup

We need some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])


Contacts Container in Setup
............................

The setup folder should contain a Contacts container:

    >>> contacts_folder = setup.get("contacts")
    >>> contacts_folder
    <Contacts at /plone/setup/contacts>

The Contacts container should be of the correct portal type:

    >>> api.get_portal_type(contacts_folder)
    'Contacts'

The Contacts container should allow Contact content types:

    >>> fti = api.get_tool("portal_types").getTypeInfo(contacts_folder)
    >>> "Contact" in fti.allowed_content_types
    True


Creating Global Contacts
.........................

Create a global contact in the setup folder:

    >>> global_contact1 = api.create(
    ...     contacts_folder,
    ...     "Contact",
    ...     Firstname="Lab",
    ...     Surname="Manager",
    ...     EmailAddress="lab.manager@senaite.com"
    ... )
    >>> global_contact1
    <Contact at /plone/setup/contacts/...>

Reindex the contact to ensure it's cataloged:

    >>> global_contact1.reindexObject()

The contact should have the correct fullname:

    >>> global_contact1.getFullname()
    'Lab Manager'

The contact should be in the contact catalog:

    >>> brains = api.search({"portal_type": "Contact", "getFullname": "Lab Manager"}, CONTACT_CATALOG)
    >>> len(brains)
    1

Create another global contact:

    >>> global_contact2 = api.create(
    ...     contacts_folder,
    ...     "Contact",
    ...     Firstname="Quality",
    ...     Surname="Manager",
    ...     EmailAddress="quality.manager@senaite.com"
    ... )
    >>> global_contact2.reindexObject()
    >>> global_contact2.getFullname()
    'Quality Manager'

Reindex the contact to ensure it's cataloged:

    >>> global_contact2.reindexObject()


Client-Specific Contacts
.........................

Create a client with its own contact:

    >>> client1 = api.create(portal.clients, "Client", Name="NARALABS", ClientID="NL")
    >>> client_contact1 = api.create(
    ...     client1,
    ...     "Contact",
    ...     Firstname="Jordi",
    ...     Surname="Puiggene",
    ...     EmailAddress="jp@naralabs.com"
    ... )
    >>> client_contact1.reindexObject()
    >>> client_contact1.getFullname()
    'Jordi Puiggene'

Create another client with a contact:

    >>> client2 = api.create(portal.clients, "Client", Name="RIDING BYTES", ClientID="RB")
    >>> client_contact2 = api.create(
    ...     client2,
    ...     "Contact",
    ...     Firstname="Ramon",
    ...     Surname="Bartl",
    ...     EmailAddress="rb@ridingbytes.com"
    ... )
    >>> client_contact2.reindexObject()
    >>> client_contact2.getFullname()
    'Ramon Bartl'


Contact Parent
...............

Global contacts should not have a client as parent:

    >>> parent = api.get_parent(global_contact1)
    >>> IClient.providedBy(parent)
    False

    >>> parent.portal_type
    'Contacts'

Client contacts should have a client as parent:

    >>> parent = api.get_parent(client_contact1)
    >>> IClient.providedBy(parent)
    True


Searching Contacts
..................

Search for all contacts:

    >>> brains = api.search({"portal_type": "Contact"}, CONTACT_CATALOG)
    >>> len(brains) == 4
    True

Search for global contacts:

    >>> brains = api.search({"portal_type": "Contact", "path": {"query": "/".join(contacts_folder.getPhysicalPath())}}, CONTACT_CATALOG)
    >>> len(brains)
    2
    >>> sorted([b.getFullname for b in brains])
    ['Lab Manager', 'Quality Manager']

Search for contacts of a specific client:

    >>> brains = api.search({"portal_type": "Contact", "path": {"query": "/".join(client1.getPhysicalPath())}}, CONTACT_CATALOG)
    >>> len(brains)
    1
    >>> brains[0].getFullname
    'Jordi Puiggene'

    >>> brains = api.search({"portal_type": "Contact", "path": {"query": "/".join(client2.getPhysicalPath())}}, CONTACT_CATALOG)
    >>> len(brains)
    1
    >>> brains[0].getFullname
    'Ramon Bartl'


Contact Listing View
.....................

The Contacts container should have a view:

    >>> view = api.get_view("view", contacts_folder, request)
    >>> view
    <...ContactsView object at ...>

The view should show all contacts:

    >>> view.catalog
    'senaite_catalog_contact'


    >>> len(view.folderitems())
    4


Contact Workflow
................

Global contacts should follow the same workflow as client contacts:

    >>> api.get_workflows_for(global_contact1)
    ('senaite_clientcontact_workflow',)

    >>> api.get_workflows_for(client_contact1)
    ('senaite_clientcontact_workflow',)

    >>> api.get_review_status(global_contact1)
    'active'

    >>> api.get_review_status(client_contact1)
    'active'


Contact Deactivation
....................

Deactivate a global contact:

    >>> _ = api.do_transition_for(global_contact1, "deactivate")
    >>> api.get_review_status(global_contact1)
    'inactive'

    >>> api.is_active(global_contact1)
    False

Reactivate the contact:

    >>> _ = api.do_transition_for(global_contact1, "activate")
    >>> api.get_review_status(global_contact1)
    'active'

    >>> api.is_active(global_contact1)
    True
