==================================
Clients, Contacts and linked Users
==================================

Clients are the customers of the lab. A client represents another company, which
has one or more natural persons as contacts.

Each contact can be linked to a Plone system user. The linking process adds the
linked user to the "Clients" group, which has the "Customer" role.

Furthermore, the user gets  the local "Owner" role for the owning client object.

Running this test from the buildout directory:

    bin/test -t ContactUser

Test Setup
==========

    >>> import transaction
    >>> from plone import api as ploneapi
    >>> from zope.lifecycleevent import modified
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

    >>> portal = self.portal
    >>> portal_url = portal.absolute_url()
    >>> bika_setup = portal.bika_setup
    >>> bika_setup_url = portal_url + "/bika_setup"
    >>> browser = self.getBrowser()
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', 'Manager', 'Owner'])

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def login(user=TEST_USER_ID, password=TEST_USER_PASSWORD):
    ...     browser.open(portal_url + "/login_form")
    ...     browser.getControl(name='__ac_name').value = user
    ...     browser.getControl(name='__ac_password').value = password
    ...     browser.getControl(name='submit').click()
    ...     assert("__ac_password" not in browser.contents)
    ...     return ploneapi.user.get_current()

    >>> def logout():
    ...     browser.open(portal_url + "/logout")
    ...     assert("You are now logged out" in browser.contents)

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)

    >>> def create(container, portal_type, title=None):
    ...     # Creates a content in a container and manually calls processForm
    ...     title = title is None and "Test {}".format(portal_type) or title
    ...     _ = container.invokeFactory(portal_type, id="tmpID", title=title)
    ...     obj = container.get(_)
    ...     obj.processForm()
    ...     modified(obj)  # notify explicitly for the test
    ...     transaction.commit()  # somehow the created method did not appear until I added this
    ...     return obj

    >>> def get_workflows_for(context):
    ...     # Returns a tuple of assigned workflows for the given context
    ...     workflow = ploneapi.portal.get_tool("portal_workflow")
    ...     return workflow.getChainFor(context)

    >>> def get_workflow_status_of(context):
    ...     # Returns the workflow status of the given context
    ...     return ploneapi.content.get_state(context)


Client
======

A `client` lives in the `/clients` folder::

    >>> clients = portal.clients
    >>> client1 = create(clients, "Client", title="Client-1")
    >>> client2 = create(clients, "Client", title="Client-2")


Contact
=======

A `contact` lives inside a `client`::

    >>> contact1 = create(client1, "Contact", "Contact-1")
    >>> contact2 = create(client2, "Contact", "Contact-2")


User
====

A `user` is able to login to the system.

Create a new user for the contact::

    >>> user1 = ploneapi.user.create(email="contact-1@example.com", username="user-1", password=TEST_USER_PASSWORD, properties=dict(fullname="Test User 1"))
    >>> user2 = ploneapi.user.create(email="contact-2@example.com", username="user-2", password=TEST_USER_PASSWORD, properties=dict(fullname="Test User 2"))
    >>> transaction.commit()


Client Browser Test
-------------------

Login with the first user::

    >>> user = login(user1.id)

The user is not allowed to access any clients folder::

    >>> browser.open(client1.absolute_url())
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Linking the user to a client contact grants access to this client::

    >>> contact1.setUser(user1)
    True
    >>> transaction.commit()

Linking a user adds this user to the `Clients` group::

    >>> clients_group = ploneapi.group.get("Clients")
    >>> user1 in clients_group.getAllGroupMembers()
    True

This gives the user the global `Client` role::

    >>> sorted(ploneapi.user.get_roles(user=user1))
    ['Authenticated', 'Client', 'Member']

It also grants local `Owner` role on the client object::

    >>> sorted(user1.getRolesInContext(client1))
    ['Authenticated', 'Member', 'Owner']

The user is able to modify the `client` object properties::

    >>> browser.open(client1.absolute_url() + "/base_edit")
    >>> "edit_form" in browser.contents
    True

As well as the `contact` object properties::

    >>> browser.open(contact1.absolute_url() + "/base_edit")
    >>> "edit_form" in browser.contents
    True

But the user can not access other clients::

    >>> browser.open(client2.absolute_url())
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Or modify other clients::

    >>> browser.open(client2.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Unlink the user revokes all access to the client::

    >>> contact1.unlinkUser()
    True
    >>> transaction.commit()

The user has no local owner role anymore on the client::

    >>> sorted(user1.getRolesInContext(client1))
    ['Authenticated', 'Member']

    >>> browser.open(client1.absolute_url())
    Traceback (most recent call last):
    ...
    Unauthorized: ...

LabContact users
================

All non-client lab users should be created as Lab Contacts in site-setup:

.. code ::

    >>> labcontact = create(portal.bika_setup.bika_labcontacts, "LabContact")

And a new user for the labcontact:

.. code ::

    >>> user3 = ploneapi.user.create(email="labmanager@example.com", username="labmanager1", password="secret", properties=dict(fullname="Lab Manager 1"))

Link the user to the labcontact:

.. code ::

    >>> labcontact.setUser(user3)
    True

Linking a user to a LabContact does not give any client group membership:

    >>> 'Client' in sorted(ploneapi.user.get_roles(user=user3)) and "Labcontact should not have the Client role!" or False
    False


Login Details View
------------------

The login details view manages to link/unlink users to contacts.

Get the `login_details` view for the first contact::

    >>> login_details_view = contact1.restrictedTraverse("login_details")

The form expects a searchstring coming from the request. We fake it here::

    >>> login_details_view.searchstring = ""

Search for linkable users:

    >>> linkable_users = login_details_view.linkable_users()
    >>> linkable_user_ids = map(lambda x: x.get("id"), linkable_users)

Both users should be now in the search results:

    >>> linkable_users = login_details_view.linkable_users()
    >>> linkable_user_ids = map(lambda x: x.get("id"), linkable_users)

    >>> user1.id in linkable_user_ids
    True

    >>> user2.id in linkable_user_ids
    True

Users with higher roles should not be listed:

    >>> setRoles(portal, "user-2", ['Member', 'Client', 'LabClerk'])

    >>> linkable_users = login_details_view.linkable_users()
    >>> linkable_user_ids = map(lambda x: x.get("id"), linkable_users)

    >>> user2.id in linkable_user_ids
    False

This contact is not linked to a user::

    >>> contact1.hasUser()
    False

Now we link a user over the view::

    >>> login_details_view._link_user(user1.id)

    >>> contact1.hasUser()
    True

The search should now omit this user from the search, so that it can not be linked anymore::

    >>> linkable_users = login_details_view.linkable_users()
    >>> linkable_user_ids = map(lambda x: x.get("id"), linkable_users)
    >>> user1.id in linkable_user_ids
    False
