===========
Permissions
===========

All objects in Bika LIMS are permission aware.
Therefore, only users with the right **roles** can view or edit contents.
Each role may contain one or more **permissions**.

Test Setup
==========

    >>> import os
    >>> import transaction
    >>> from plone import api as ploneapi
    >>> from zope.lifecycleevent import modified
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

    >>> portal = self.portal
    >>> portal_url = portal.absolute_url()
    >>> bika_setup = portal.bika_setup
    >>> bika_setup_url = portal_url + "/bika_setup"
    >>> browser = self.getBrowser()

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


Test Workflows and Permissions
==============================

Workflows control the allowed roles for specific permissions.
A role is a container for several permissions.


Bika Setup
----------

Bika Setup is a folderish object, which handles the labs' configuration items, like
Laboratory information, Instruments, Analysis Services etc.

Test Workflow
.............

A `bika_setup` lives in the root of a bika installation, or more precisely, the
portal object::

    >>> bika_setup = portal.bika_setup

The `setup` folder follows the `senaite_setup_workflow` and is initially in the
`active` state::

    >>> get_workflows_for(bika_setup)
    ('senaite_setup_workflow',)

    >>> get_workflow_status_of(bika_setup)
    'active'

Test Permissions
................

Exactly these roles have should have a `View` permission::

    >>> get_roles_for_permission("View", bika_setup)
    ['Authenticated']

Exactly these roles have should have the `Access contents information` permission::

    >>> get_roles_for_permission("Access contents information", bika_setup)
    ['Authenticated']

Exactly these roles have should have the `List folder contents` permission::

    >>> get_roles_for_permission("List folder contents", bika_setup)
    ['Authenticated']

Exactly these roles have should have the `Modify portal content` permission::

    >>> get_roles_for_permission("Modify portal content", bika_setup)
    ['LabClerk', 'LabManager', 'Manager']

Exactly these roles (nobody) should have the `Delete objects` permission::

    >>> get_roles_for_permission("Delete objects", bika_setup)
    []

Anonymous Browser Test
......................

Ensure we are logged out::

    >>> logout()

Anonymous should not be able to view the `bika_setup` folder::

    >>> browser.open(bika_setup.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit the `bika_setup` folder::

    >>> browser.open(bika_setup.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...


Laboratory
----------

The Laboratory object holds all needed information about the lab itself.
It lives inside the `bika_setup` folder.

Test Workflow
.............

A `laboratory` lives in the root of a bika installation, or more precisely, the
portal object::

    >>> laboratory = portal.bika_setup.laboratory

The `laboratory` folder follows the `senaite_laboratory_workflow` and is
initially in the `active` state::

    >>> get_workflows_for(laboratory)
    ('senaite_laboratory_workflow',)

    >>> get_workflow_status_of(laboratory)
    'active'

Test Permissions
................

Exactly these roles have should have a `View` permission::

    >>> get_roles_for_permission("View", laboratory)
    ['Authenticated']

Exactly these roles have should have the `Access contents information` permission::

    >>> get_roles_for_permission("Access contents information", laboratory)
    ['Authenticated']

Exactly these roles have should have the `List folder contents` permission::

    >>> get_roles_for_permission("List folder contents", laboratory)
    ['Authenticated']

Exactly these roles have should have the `Modify portal content` permission::

    >>> get_roles_for_permission("Modify portal content", laboratory)
    ['LabClerk', 'LabManager', 'Manager']

Exactly these roles (nobody) should have the `Delete objects` permission::

    >>> get_roles_for_permission("Delete objects", laboratory)
    []

Anonymous Browser Test
......................

Ensure we are logged out::

    >>> logout()

Anonymous should not be able to view the `laboratory` folder::

    >>> browser.open(laboratory.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit the `laboratory` folder::

    >>> browser.open(laboratory.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...


Lab Contact(s)
--------------

Lab Contacts are the employees of the lab.

Test Workflow
.............

A `labcontact` lives in the `bika_setup/bika_labcontacts` folder::

    >>> labcontacts = bika_setup.bika_labcontacts
    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> labcontact = create(labcontacts, "LabContact")

The `bika_labcontacts` folder follows the `senaite_one_state_workflow` and is
initially in the `active` state::

    >>> get_workflows_for(labcontacts)
    ('senaite_one_state_workflow',)

    >>> get_workflow_status_of(labcontacts)
    'active'

A `labcontact` follows the `senaite_deactivable_type_workflow` and has an initial state of `active`::

    >>> get_workflows_for(labcontact)
    ('senaite_labcontact_workflow',)

    >>> get_workflow_status_of(labcontacts)
    'active'

Test Permissions
................

Exactly these roles have should have a `View` permission::

    >>> get_roles_for_permission("View", labcontacts)
    ['Authenticated']

    >>> get_roles_for_permission("View", labcontact)
    ['LabClerk', 'LabManager', 'Manager', 'Publisher']

Exactly these roles have should have the `Access contents information` permission::

    >>> get_roles_for_permission("Access contents information", labcontacts)
    ['Authenticated']

    >>> get_roles_for_permission("Access contents information", labcontact)
    ['Authenticated']

Exactly these roles have should have the `List folder contents` permission::

    >>> get_roles_for_permission("List folder contents", labcontacts)
    ['Authenticated']

    >>> get_roles_for_permission("List folder contents", labcontact)
    []

Exactly these roles have should have the `Modify portal content` permission::

    >>> get_roles_for_permission("Modify portal content", labcontacts)
    ['LabClerk', 'LabManager', 'Manager']

    >>> get_roles_for_permission("Modify portal content", labcontact)
    ['LabClerk', 'LabManager', 'Manager']

Exactly these roles have should have the `Delete objects` permission::

    >>> get_roles_for_permission("Delete objects", labcontacts)
    []

    >>> get_roles_for_permission("Delete objects", labcontact)
    []

Anonymous Browser Test
......................

Ensure we are logged out::

    >>> logout()

Anonymous should not be able to view the `bika_labcontacts` folder::

    >>> browser.open(labcontacts.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to view a `labcontact`::

    >>> browser.open(labcontact.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit the `bika_labcontacts` folder::

    >>> browser.open(labcontacts.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit a `labcontact`::

    >>> browser.open(labcontact.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...


Clients and Contacts
--------------------

Clients are the customers of the lab. A client represents another company, which
has one or more natural persons as contacts.

Test Workflow
.............

A `client` lives in the `/clients` folder::

    >>> clients = portal.clients
    >>> client = create(clients, "Client")
    >>> another_client = create(clients, "Client")

A `contact` lives in a `client`::

    >>> contact = create(client, "Contact")

The `clients` folder follows `senaite_clients_workflow` workflow::

    >>> get_workflows_for(clients)
    ('senaite_clients_workflow',)

A `client` follows the `senaite_client_workflow` and has an initial state of
`active`::

    >>> get_workflows_for(client)
    ('senaite_client_workflow',)

    >>> get_workflow_status_of(client)
    'active'

A `contact` follows the `senaite_deactivable_type_workflow` and has an initial
state of `active`::

    >>> get_workflows_for(contact)
    ('senaite_clientcontact_workflow',)

    >>> get_workflow_status_of(contact)
    'active'

Test Permissions
................

Exactly these roles have should have a `View` permission for clients folder::

    >>> get_roles_for_permission("View", clients)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Owner', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

Exactly these roles should have a `View` permission for client object. Note that
permissions for Client role are not granted, but for Owner. Lab Contacts are
Owners of the Client they belong to, so client contacts only have access to the
Client they belong to:

    >>> get_roles_for_permission("View", client)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Owner', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

Exactly these roles should have a `View` permission for client contact object:

    >>> get_roles_for_permission("View", contact)
    ['LabClerk', 'LabManager', 'Manager', 'Owner', 'Publisher']

Exactly these roles have should have the `Access contents information` permission::

    >>> get_roles_for_permission("Access contents information", clients)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Owner', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

    >>> get_roles_for_permission("Access contents information", client)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Owner', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

    >>> get_roles_for_permission("Access contents information", contact)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Owner', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

Exactly these roles have should have the `List folder contents` permission::

    >>> get_roles_for_permission("List folder contents", clients)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Owner', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

    >>> get_roles_for_permission("List folder contents", client)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Owner', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

    >>> get_roles_for_permission("List folder contents", contact)
    []

Exactly these roles have should have the `Modify portal content` permission::

    >>> get_roles_for_permission("Modify portal content", clients)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> get_roles_for_permission("Modify portal content", client)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

Exactly these roles have should have the `Delete objects` permission::

    >>> get_roles_for_permission("Delete objects", clients)
    []

    >>> get_roles_for_permission("Delete objects", client)
    []

Anonymous Browser Test
......................

Ensure we are logged out::

    >>> logout()

Anonymous should be able to view the `clients` folder::

    >>> browser.open(clients.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to view a `client`::

    >>> browser.open(client.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit the `bika_clients` folder::

    >>> browser.open(clients.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit a `client`::

    >>> browser.open(client.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Client Contacts Browser Test
............................

Create a new user for the contact::

    >>> user = ploneapi.user.create(email="contact-1@client-1.com", username="contact-1", password=TEST_USER_PASSWORD, properties=dict(fullname="Test Contact 1"))
    >>> transaction.commit()

Now we log in as the new user::

    >>> login(user.id)

The user can not access the clients folder yet::

    >>> browser.open(clients.absolute_url())
    Traceback (most recent call last):
    ...
    Unauthorized: ...

    >>> browser.open(client.absolute_url())
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Link the user to a client contact to grant access to this client::

    >>> contact.setUser(user)
    True
    >>> transaction.commit()

Linking a user adds this user to the `Clients` group::

    >>> clients_group = ploneapi.group.get("Clients")
    >>> user in clients_group.getAllGroupMembers()
    True

This gives the user the global `Client` role::

    >>> sorted(ploneapi.user.get_roles(user=user))
    ['Authenticated', 'Client', 'Member']

It also grants local `Owner` role on the client object::

    >>> sorted(user.getRolesInContext(client))
    ['Authenticated', 'Member', 'Owner']

The user is able to modify the client properties::

    >>> browser.open(client.absolute_url() + "/base_edit")
    >>> "edit_form" in browser.contents
    True

As well as the own contact properties::

    >>> browser.open(contact.absolute_url() + "/base_edit")
    >>> "edit_form" in browser.contents
    True

But the user can not access other clients::

    >>> browser.open(another_client.absolute_url())
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Or modify other clients::

    >>> browser.open(another_client.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Unlink the user to revoke all access to the client::

    >>> contact.unlinkUser()
    True
    >>> transaction.commit()

The user has no local owner role anymore on the client::

    >>> sorted(user.getRolesInContext(client))
    ['Authenticated', 'Member']

The user can not access the client anymore::

    >>> browser.open(clients.absolute_url())
    Traceback (most recent call last):
    ...
    Unauthorized: ...

    >>> browser.open(client.absolute_url())
    Traceback (most recent call last):
    ...
    Unauthorized: ...


Instrument(s)
-------------

Instruments represent the measuring hardware of the lab.

Test Workflow
.............

A `instrument` lives in the `bika_setup/bika_instruments` folder::

    >>> instruments = bika_setup.bika_instruments
    >>> instrument = create(instruments, "Instrument")

The `bika_instruments` folder follows the `senaite_one_state_workflow` and is
initially in the `active` state::

    >>> get_workflows_for(instruments)
    ('senaite_instruments_workflow',)

    >>> get_workflow_status_of(instruments)
    'active'

A `instrument` follows the `senaite_deactivable_type_workflow` and has an
initial state of `active`::

    >>> get_workflows_for(instrument)
    ('senaite_deactivable_type_workflow',)

    >>> get_workflow_status_of(instruments)
    'active'

Test Permissions
................

Exactly these roles have should have a `View` permission::

    >>> get_roles_for_permission("View", instruments)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

    >>> get_roles_for_permission("View", instrument)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

Exactly these roles have should have the `Access contents information` permission::

    >>> get_roles_for_permission("Access contents information", instruments)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

    >>> get_roles_for_permission("Access contents information", instrument)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

Exactly these roles have should have the `List folder contents` permission::

    >>> get_roles_for_permission("List folder contents", instruments)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

    >>> get_roles_for_permission("List folder contents", instrument)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Preserver', 'Publisher', 'RegulatoryInspector', 'Sampler', 'SamplingCoordinator', 'Verifier']

Exactly these roles have should have the `Modify portal content` permission::

    >>> get_roles_for_permission("Modify portal content", instruments)
    ['LabClerk', 'LabManager', 'Manager']

    >>> get_roles_for_permission("Modify portal content", instrument)
    ['LabClerk', 'LabManager', 'Manager']

Exactly these roles have should have the `Delete objects` permission::

    >>> get_roles_for_permission("Delete objects", instruments)
    []

    >>> get_roles_for_permission("Delete objects", instrument)
    []

Anonymous Browser Test
......................

Ensure we are logged out::

    >>> logout()

Anonymous should not be able to view the `bika_instruments` folder::

    >>> browser.open(instruments.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to view a `instrument`::

    >>> browser.open(instrument.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit the `bika_instruments` folder::

    >>> browser.open(instruments.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit a `instrument`::

    >>> browser.open(instrument.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...


Method(s)
---------

Methods describe the sampling methods of the lab.

Methods should be viewable by unauthenticated users for information purpose.


Test Workflow
.............

A `method` lives in the `methods` folder::

    >>> methods = portal.methods
    >>> method = create(methods, "Method")

The `methods` folder follows the `senaite_setup_workflow` and is initially in
the `active` state::

    >>> get_workflows_for(methods)
    ('senaite_setup_workflow',)

    >>> get_workflow_status_of(methods)
    'active'

A `method` follows the `senaite_deactivable_type_workflow` and has an initial
state of `active`::

    >>> get_workflows_for(method)
    ('senaite_deactivable_type_workflow',)

    >>> get_workflow_status_of(methods)
    'active'

Test Permissions
................

Exactly these roles have should have a `View` permission::

    >>> get_roles_for_permission("View", methods)
    ['Authenticated']

    >>> get_roles_for_permission("View", method)
    ['Authenticated']

Exactly these roles have should have the `Access contents information` permission::

    >>> get_roles_for_permission("Access contents information", methods)
    ['Authenticated']

    >>> get_roles_for_permission("Access contents information", method)
    ['Authenticated']

Exactly these roles have should have the `List folder contents` permission::

    >>> get_roles_for_permission("List folder contents", methods)
    ['Authenticated']

    >>> get_roles_for_permission("List folder contents", method)
    ['Authenticated']

Exactly these roles have should have the `Modify portal content` permission::

    >>> get_roles_for_permission("Modify portal content", methods)
    ['LabClerk', 'LabManager', 'Manager']

    >>> get_roles_for_permission("Modify portal content", method)
    ['LabClerk', 'LabManager', 'Manager']

Exactly these roles have should have the `Delete objects` permission::

    >>> get_roles_for_permission("Delete objects", methods)
    []

    >>> get_roles_for_permission("Delete objects", method)
    []

Anonymous Browser Test
......................

Ensure we are logged out::

    >>> logout()

Anonymous should not be able to view the `methods` folder::

    >>> browser.open(methods.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to view a `method`::

    >>> browser.open(method.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit the `methods` folder::

    >>> browser.open(methods.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit a `method`::

    >>> browser.open(method.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...


Analysis Service(s)
-------------------

Analysis services describe which "products" the lab offers.

Test Workflow
.............

A `analysisservice` lives in the `bika_setup/bika_analysisservices` folder::

    >>> analysisservices = bika_setup.bika_analysisservices
    >>> analysisservice = create(analysisservices, "AnalysisService")

The `bika_analysisservices` folder follows the `senaite_one_state_workflow`
and is initially in the `active` state::

    >>> get_workflows_for(analysisservices)
    ('senaite_one_state_workflow',)

    >>> get_workflow_status_of(analysisservices)
    'active'

A `analysisservice` follows the `senaite_deactivable_type_workflow` and has an
initial state of `active`::

    >>> get_workflows_for(analysisservice)
    ('senaite_deactivable_type_workflow',)

    >>> get_workflow_status_of(analysisservices)
    'active'

Test Permissions
................

Exactly these roles have should have a `View` permission::

    >>> get_roles_for_permission("View", analysisservices)
    ['Authenticated']

    >>> get_roles_for_permission("View", analysisservice)
    ['Authenticated']

Exactly these roles have should have the `Access contents information` permission::

    >>> get_roles_for_permission("Access contents information", analysisservices)
    ['Authenticated']

    >>> get_roles_for_permission("Access contents information", analysisservice)
    ['Authenticated']

Exactly these roles have should have the `List folder contents` permission::

    >>> get_roles_for_permission("List folder contents", analysisservices)
    ['Authenticated']

    >>> get_roles_for_permission("List folder contents", analysisservice)
    ['Authenticated']

Exactly these roles have should have the `Modify portal content` permission::

    >>> get_roles_for_permission("Modify portal content", analysisservices)
    ['LabClerk', 'LabManager', 'Manager']

    >>> get_roles_for_permission("Modify portal content", analysisservice)
    ['LabClerk', 'LabManager', 'Manager']

Exactly these roles have should have the `Delete objects` permission::

    >>> get_roles_for_permission("Delete objects", analysisservices)
    []

    >>> get_roles_for_permission("Delete objects", analysisservice)
    []

Anonymous Browser Test
......................

Ensure we are logged out::

    >>> logout()

Anonymous should not be able to view the `bika_analysisservices` folder::

    >>> browser.open(analysisservices.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous are **not** allowed to view an `analysisservice`::

    >>> browser.open(analysisservice.absolute_url() + "/base_view")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit the `bika_analysisservices` folder::

    >>> browser.open(analysisservices.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

Anonymous should not be able to edit a `analysisservice`::

    >>> browser.open(analysisservice.absolute_url() + "/base_edit")
    Traceback (most recent call last):
    ...
    Unauthorized: ...

