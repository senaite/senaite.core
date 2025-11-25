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

Test fixture - why is the `Name` not set?

    >>> client1.setName("NARALABS")

Test continuation:

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

Test fixture - why is the `Name` not set?

    >>> client2.setName("RIDING BYTES")

Test continuation:

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

The view should use the contact catalog:

    >>> view.catalog
    'senaite_catalog_contact'

By default, the view shows only global contacts:

    >>> len(view.folderitems())
    2

The view should include the Location column:

    >>> "Location" in view.columns
    True

The Location column should show the contacts folder name for global contacts:

    >>> items = view.folderitems()
    >>> global_contact_items = [i for i in items if i.get("getFullname") == "Lab Manager"]
    >>> len(global_contact_items)
    1
    >>> global_contact_items[0]["Location"]
    'Contacts'

When the include_client_contacts cookie is set, the view shows all contacts:

    >>> request.cookies["include_client_contacts"] = "1"
    >>> view = api.get_view("view", contacts_folder, request)
    >>> len(view.folderitems())
    4

The Location column should show the client name for client contacts:

    >>> items = view.folderitems()
    >>> client1_contact_items = [i for i in items if i.get("getFullname") == "Jordi Puiggene"]
    >>> len(client1_contact_items)
    1
    >>> client1_contact_items[0]["Location"]
    'NARALABS'

    >>> client2_contact_items = [i for i in items if i.get("getFullname") == "Ramon Bartl"]
    >>> len(client2_contact_items)
    1
    >>> client2_contact_items[0]["Location"]
    'RIDING BYTES'


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


User Linking for Global Contacts
..................................

Global contacts can be linked to source users, similar to client contacts.
However, linking a user to a global contact does NOT grant the Client role,
since global contacts are not associated with a specific client.

First, verify that global contacts are identified as global:

    >>> global_contact1.isGlobal()
    True

    >>> client_contact1.isGlobal()
    False

Create test users for linking:

    >>> from plone import api as ploneapi
    >>> import transaction
    >>> from plone.app.testing import TEST_USER_PASSWORD

    >>> global_user1 = ploneapi.user.create(
    ...     email="global.user1@example.com",
    ...     username="global-user-1",
    ...     password=TEST_USER_PASSWORD,
    ...     properties=dict(fullname="Global User 1")
    ... )
    >>> global_user2 = ploneapi.user.create(
    ...     email="global.user2@example.com",
    ...     username="global-user-2",
    ...     password=TEST_USER_PASSWORD,
    ...     properties=dict(fullname="Global User 2")
    ... )
    >>> transaction.commit()

Initially, the global contact has no linked user:

    >>> global_contact1.hasUser()
    False

    >>> global_contact1.getUser() is None
    True

Link a user to the global contact:

    >>> global_contact1.setUser(global_user1)
    True

    >>> global_contact1.hasUser()
    True

The linked user should now be associated with the contact:

    >>> user_obj = global_contact1.getUser()
    >>> user_obj is not None
    True

    >>> user_obj.getId()
    'global-user-1'

Verify the username is stored on the contact:

    >>> global_contact1.getUsername()
    'global-user-1'

Global contacts do NOT grant Client role to linked users:

    >>> sorted(ploneapi.user.get_roles(user=global_user1))
    ['Authenticated', 'Member']

Global contacts are not associated with a client group:

    >>> 'Client' in ploneapi.user.get_roles(user=global_user1)
    False

Unlink the user from the global contact:

    >>> global_contact1._unlinkUser()
    True

    >>> global_contact1.hasUser()
    False

    >>> global_contact1.getUser() is None
    True

    >>> global_contact1.getUsername()
    ''


Login Details View for Global Contacts
........................................

The login_details view manages linking/unlinking users to global contacts.

Get the login_details view for the global contact:

    >>> login_details_view = global_contact1.restrictedTraverse("login_details")

The form expects a searchstring from the request. We fake it here:

    >>> login_details_view.searchstring = ""

Check if this is a global contact (not a client contact):

    >>> login_details_view.is_contact()
    True

    >>> login_details_view.is_labcontact()
    False

Search for linkable users (users not already linked to a contact):

    >>> linkable_users = login_details_view.linkable_users()
    >>> linkable_user_ids = [u.get("id") for u in linkable_users]

Our test users should be in the search results:

    >>> global_user1.getId() in linkable_user_ids
    True

    >>> global_user2.getId() in linkable_user_ids
    True

Link a user via the view:

    >>> login_details_view._link_user(global_user1.getId())

The contact should now have a linked user:

    >>> global_contact1.hasUser()
    True

The linked user should be omitted from the search results:

    >>> linkable_users = login_details_view.linkable_users()
    >>> linkable_user_ids = [u.get("id") for u in linkable_users]
    >>> global_user1.getId() in linkable_user_ids
    False

Unlink the user via the view:

    >>> login_details_view._unlink_user()

    >>> global_contact1.hasUser()
    False


My Organization View Availability
...................................

The my_organization view has an available() method that determines if it should
be shown in the navigation. It should NOT be available for global contacts.

First, link a user to a global contact:

    >>> global_contact1.setUser(global_user1)
    True

Get the my_organization view:

    >>> my_org_view = global_contact1.restrictedTraverse("my_organization")

The view should NOT be available for users linked to global contacts:

    >>> my_org_view.available()
    False

Now test with a client contact user. First, create a new user for the client contact:

    >>> client_user1 = ploneapi.user.create(
    ...     email="client.user1@example.com",
    ...     username="client-user-1",
    ...     password=TEST_USER_PASSWORD,
    ...     properties=dict(fullname="Client User 1")
    ... )
    >>> transaction.commit()

Link the user to the client contact:

    >>> client_contact1.setUser(client_user1)
    True

Get the my_organization view for the client contact:

    >>> client_my_org_view = client_contact1.restrictedTraverse("my_organization")

The view should be available for users linked to client contacts:

    >>> client_my_org_view.available()
    True
