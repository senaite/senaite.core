================
SENAITE LIMS API
================

The SENAITE LIMS API provides single functions for single purposes.
This Test builds completely on the API without any further imports needed.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API

API
===

The purpose of this API is to help coders to follow the DRY principle (Don't
Repeat Yourself). It also ensures that the most effective and efficient method is
used to achieve a task.

Import it first::

    >>> from bika.lims import api


Setup the test user
-------------------

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Getting the Portal
------------------

The Portal is the SENAITE LIMS root object::

    >>> portal = api.get_portal()
    >>> portal
    <PloneSite at /plone>


Getting the SENAITE Setup object
--------------------------------

The Setup object gives access to all of the SENAITE configuration settings::

    >>> setup = api.get_setup()
    >>> setup
    <BikaSetup at /plone/bika_setup>

    >>> bika_setup = api.get_bika_setup()
    >>> setup
    <BikaSetup at /plone/bika_setup>

    >>> setup == bika_setup
    True


Creating new Content
--------------------

Creating new contents in SENAITE LIMS requires some special knowledge.
This function helps to do it right and creates a content for you.

Here we create a new `Client` in the `plone/clients` folder::

    >>> client = api.create(portal.clients, "Client", title="Test Client")
    >>> client
    <Client at /plone/clients/client-1>

     >>> client.Title()
     'Test Client'


Getting a Tool
--------------

There are many ways to get a tool in SENAITE LIMS / Plone. This function
centralizes this functionality and makes it painless::

    >>> api.get_tool("bika_setup_catalog")
    <BikaSetupCatalog at /plone/bika_setup_catalog>

Trying to fetch an non-existing tool raises a custom `APIError`.

    >>> api.get_tool("NotExistingTool")
    Traceback (most recent call last):
    [...]
    APIError: No tool named 'NotExistingTool' found.

This error can also be used for custom methods with the `fail` function::

    >>> api.fail("This failed badly")
    Traceback (most recent call last):
    [...]
    APIError: This failed badly


Getting an Object
-----------------

Getting the object from a catalog brain is a common task.

This function provides an unified interface to portal objects **and** brains.
Furthermore it is idempotent, so it can be called multiple times in a row::

We will demonstrate the usage on the client object we created above::

    >>> api.get_object(client)
    <Client at /plone/clients/client-1>

    >>> api.get_object(api.get_object(client))
    <Client at /plone/clients/client-1>

Now we show it with catalog results::

    >>> portal_catalog = api.get_tool("portal_catalog")
    >>> brains = portal_catalog(portal_type="Client")
    >>> brains
    [<Products.ZCatalog.Catalog.mybrains object at 0x...>]

    >>> brain = brains[0]

    >>> api.get_object(brain)
    <Client at /plone/clients/client-1>

    >>> api.get_object(api.get_object(brain))
    <Client at /plone/clients/client-1>

The function also accepts a UID:

    >>> api.get_object(api.get_uid(brain))
    <Client at /plone/clients/client-1>

And returns the portal object when UID=="0"

    >>> api.get_object("0")
    <PloneSite at /plone>

No supported objects raise an error::

    >>> api.get_object(object())
    Traceback (most recent call last):
    [...]
    APIError: <object object at 0x...> is not supported.

    >>> api.get_object("i_am_not_an_uid")
    Traceback (most recent call last):
    [...]
    APIError: 'i_am_not_an_uid' is not supported.

However, if a `default` value is provided, the default will be returned in such
a case instead:

    >>> api.get_object(object(), default=None) is None
    True

To check if an object is supported, e.g. is an ATCT, Dexterity, ZCatalog or
Portal object, we can use the `is_object` function::

    >>> api.is_object(client)
    True

    >>> api.is_object(brain)
    True

    >>> api.is_object(api.get_portal())
    True

    >>> api.is_object(None)
    False

    >>> api.is_object(object())
    False


Checking if an Object is the Portal
-----------------------------------

Sometimes it can be handy to check if the current object is the portal::

    >>> api.is_portal(portal)
    True

    >>> api.is_portal(client)
    False

    >>> api.is_portal(object())
    False


Checking if an Object is a Catalog Brain
----------------------------------------

Knowing if we have an object or a brain can be handy. This function checks this for you::

    >>> api.is_brain(brain)
    True

    >>> api.is_brain(api.get_object(brain))
    False

    >>> api.is_brain(object())
    False


Checking if an Object is a Dexterity Content
--------------------------------------------

This function checks if an object is a `Dexterity` content type::

    >>> api.is_dexterity_content(client)
    False

    >>> api.is_dexterity_content(portal)
    False

We currently have no `Dexterity` contents, so testing this comes later...


Checking if an Object is an AT Content
--------------------------------------

This function checks if an object is an `Archetypes` content type::

    >>> api.is_at_content(client)
    True

    >>> api.is_at_content(portal)
    False

    >>> api.is_at_content(object())
    False


Getting the Schema of a Content
-------------------------------

The schema contains the fields of a content object. Getting the schema is a
common task, but differs between `ATContentType` based objects and `Dexterity`
based objects. This function brings it under one umbrella::

    >>> schema = api.get_schema(client)
    >>> schema
    <Products.Archetypes.Schema.Schema object at 0x...>

Catalog brains are also supported::

    >>> api.get_schema(brain)
    <Products.Archetypes.Schema.Schema object at 0x...>


Getting the Fields of a Content
-------------------------------

The fields contain all the values that an object holds and are therefore
responsible for getting and setting the information.

This function returns the fields as a dictionary mapping of `{"key": value}`::

    >>> fields = api.get_fields(client)
    >>> fields.get("ClientID")
    <Field ClientID(string:rw)>

Catalog brains are also supported::

    >>> api.get_fields(brain).get("ClientID")
    <Field ClientID(string:rw)>


Getting the ID of a Content
---------------------------

Getting the ID is a common task in SENAITE LIMS.
This function takes care that catalog brains are not woken up for this task::

    >>> api.get_id(portal)
    'plone'

    >>> api.get_id(client)
    'client-1'

    >>> api.get_id(brain)
    'client-1'


Getting the Title of a Content
------------------------------

Getting the Title is a common task in SENAITE LIMS.
This function takes care that catalog brains are not woken up for this task::

    >>> api.get_title(portal)
    u'Plone site'

    >>> api.get_title(client)
    'Test Client'

    >>> api.get_title(brain)
    'Test Client'


Getting the Description of a Content
------------------------------------

Getting the Description is a common task in SENAITE LIMS.
This function takes care that catalog brains are not woken up for this task::

    >>> api.get_description(portal)
    ''

    >>> api.get_description(client)
    ''

    >>> api.get_description(brain)
    ''


Getting the UID of a Content
----------------------------

Getting the UID is a common task in SENAITE LIMS.
This function takes care that catalog brains are not woken up for this task.

The portal object actually has no UID. This funciton defines it therefore to be `0`::

    >>> api.get_uid(portal)
    '0'

    >>> uid_client = api.get_uid(client)
    >>> uid_client_brain = api.get_uid(brain)
    >>> uid_client is uid_client_brain
    True

If a UID is passed to the function, it will return the value unchanged:

    >>> api.get_uid(uid_client) == uid_client
    True



Getting the URL of a Content
----------------------------

Getting the URL is a common task in SENAITE LIMS.
This function takes care that catalog brains are not woken up for this task::

    >>> api.get_url(portal)
    'http://nohost/plone'

    >>> api.get_url(client)
    'http://nohost/plone/clients/client-1'

    >>> api.get_url(brain)
    'http://nohost/plone/clients/client-1'


Getting the Icon of a Content
-----------------------------

    >>> api.get_icon(client)
    '<img width="16" height="16" src="http://nohost/plone/++resource++bika.lims.images/client.png" title="Test Client" />'

    >>> api.get_icon(brain)
    '<img width="16" height="16" src="http://nohost/plone/++resource++bika.lims.images/client.png" title="Test Client" />'

    >>> api.get_icon(client, html_tag=False)
    'http://nohost/plone/++resource++bika.lims.images/client.png'

    >>> api.get_icon(client, html_tag=False)
    'http://nohost/plone/++resource++bika.lims.images/client.png'


Getting a catalog brain by UID
------------------------------

This function finds a catalog brain by its uinique ID (UID)::

    >>> api.get_brain_by_uid(api.get_uid(client))
    <Products.Archetypes.UIDCatalog.plugbrains object at ...>


Getting an object by UID
------------------------

This function finds an object by its uinique ID (UID).
The portal object with the defined UId of '0' is also supported::

    >>> api.get_object_by_uid('0')
    <PloneSite at /plone>

    >>> api.get_object_by_uid(uid_client)
    <Client at /plone/clients/client-1>

    >>> api.get_object_by_uid(uid_client_brain)
    <Client at /plone/clients/client-1>

If a default value is provided, the function will never fail.  Any exception
or error will result in the default value being returned::

    >>> api.get_object_by_uid('invalid uid', 'default')
    'default'

    >>> api.get_object_by_uid(None, 'default')
    'default'


Getting an object by Path
-------------------------

This function finds an object by its physical path::

    >>> api.get_object_by_path('/plone')
    <PloneSite at /plone>

    >>> api.get_object_by_path('/plone/clients/client-1')
    <Client at /plone/clients/client-1>

Paths outside the portal raise an error::

    >>> api.get_object_by_path('/root')
    Traceback (most recent call last):
    [...]
    APIError: Not a physical path inside the portal.

Any exception returns default value::

    >>> api.get_object_by_path('/invaid/path', 'default')
    'default'

    >>> api.get_object_by_path(None, 'default')
    'default'


Getting the Physical Path of an Object
--------------------------------------

The physical path describes exactly where an object is located inside the portal.
This function unifies the different approaches to get the physical path and does
so in the most efficient way::

    >>> api.get_path(portal)
    '/plone'

    >>> api.get_path(client)
    '/plone/clients/client-1'

    >>> api.get_path(brain)
    '/plone/clients/client-1'

    >>> api.get_path(object())
    Traceback (most recent call last):
    [...]
    APIError: <object object at 0x...> is not supported.


Getting the Physical Parent Path of an Object
---------------------------------------------

This function returns the physical path of the parent object::

    >>> api.get_parent_path(client)
    '/plone/clients'

    >>> api.get_parent_path(brain)
    '/plone/clients'

However, this function goes only up to the portal object::

    >>> api.get_parent_path(portal)
    '/plone'

Like with the other functions, only portal objects are supported::

    >>> api.get_parent_path(object())
    Traceback (most recent call last):
    [...]
    APIError: <object object at 0x...> is not supported.


Getting the Parent Object
-------------------------

This function returns the parent object::

    >>> api.get_parent(client)
    <ClientFolder at /plone/clients>

Brains are also supported::

    >>> api.get_parent(brain)
    <ClientFolder at /plone/clients>

The function can also use a catalog query on the `portal_catalog` and return a
brain, if the passed parameter `catalog_search` was set to true. ::

    >>> api.get_parent(client, catalog_search=True)
    <Products.ZCatalog.Catalog.mybrains object at 0x...>

    >>> api.get_parent(brain, catalog_search=True)
    <Products.ZCatalog.Catalog.mybrains object at 0x...>

However, this function goes only up to the portal object::

    >>> api.get_parent(portal)
    <PloneSite at /plone>

Like with the other functions, only portal objects are supported::

    >>> api.get_parent(object())
    Traceback (most recent call last):
    [...]
    APIError: <object object at 0x...> is not supported.


Searching Objects
-----------------

Searching in SENAITE LIMS requires knowledge in which catalog the object is indexed.
This function unifies all SENAITE LIMS catalog to a single search interface::

    >>> results = api.search({'portal_type': 'Client'})
    >>> results
    [<Products.ZCatalog.Catalog.mybrains object at 0x...>]

Multiple content types are also supported::

    >>> results = api.search({'portal_type': ['Client', 'ClientFolder'], 'sort_on': 'getId'})
    >>> map(api.get_id, results)
    ['client-1', 'clients']

Now we create some objects which are located in the `bika_setup_catalog`::

    >>> instruments = bika_setup.bika_instruments
    >>> instrument1 = api.create(instruments, "Instrument", title="Instrument-1")
    >>> instrument2 = api.create(instruments, "Instrument", title="Instrument-2")
    >>> instrument3 = api.create(instruments, "Instrument", title="Instrument-3")

    >>> results = api.search({'portal_type': 'Instrument', 'sort_on': 'getId'})
    >>> len(results)
    3

    >>> map(api.get_id, results)
    ['instrument-1', 'instrument-2', 'instrument-3']

Queries which result in multiple catalogs will be refused, as it would require
manual merging and sorting of the results afterwards. Thus, we fail here:

    >>> results = api.search({'portal_type': ['Client', 'ClientFolder', 'Instrument'], 'sort_on': 'getId'})
    Traceback (most recent call last):
    [...]
    APIError: Multi Catalog Queries are not supported!

Catalog queries w/o any `portal_type`, default to the `portal_catalog`, which
will not find the following items::

    >>> analysiscategories = bika_setup.bika_analysiscategories
    >>> analysiscategory1 = api.create(analysiscategories, "AnalysisCategory", title="AC-1")
    >>> analysiscategory2 = api.create(analysiscategories, "AnalysisCategory", title="AC-2")
    >>> analysiscategory3 = api.create(analysiscategories, "AnalysisCategory", title="AC-3")

    >>> results = api.search({"id": "analysiscategory-1"})
    >>> len(results)
    0

Would we add the `portal_type`, the search function would ask the
`archetype_tool` for the right catalog, and it would return a result::

    >>> results = api.search({"portal_type": "AnalysisCategory", "id": "analysiscategory-1"})
    >>> len(results)
    1

We could also explicitly define a catalog to achieve the same::

    >>> results = api.search({"id": "analysiscategory-1"}, catalog="bika_setup_catalog")
    >>> len(results)
    1

To see inactive or dormant items, we must explicitly query them of filter them
afterwars manually::

    >>> results = api.search({"portal_type": "AnalysisCategory", "id": "analysiscategory-1"})
    >>> len(results)
    1

Now we deactivate the item::

    >>> analysiscategory1 = api.do_transition_for(analysiscategory1, 'deactivate')
    >>> api.is_active(analysiscategory1)
    False

The search will still find the item::

    >>> results = api.search({"portal_type": "AnalysisCategory", "id": "analysiscategory-1"})
    >>> len(results)
    1

Unless we filter it out manually::

    >>> len(filter(api.is_active, results))
    0

Or provide a correct query::

    >>> results = api.search({"portal_type": "AnalysisCategory", "id": "analysiscategory-1", "is_active": False})
    >>> len(results)
    1


Getting the registered Catalogs
-------------------------------

SENAITE LIMS uses multiple catalogs registered via the Archetype Tool. This
function returns a list of registered catalogs for a brain or object::

    >>> api.get_catalogs_for(client)
    [...]

    >>> api.get_catalogs_for(instrument1)
    [...]

    >>> api.get_catalogs_for(analysiscategory1)
    [...]


Getting an Attribute of an Object
---------------------------------

This function handles attributes and methods the same and returns their value.
It also handles security and is able to return a default value instead of
raising an `Unauthorized` error::

    >>> uid_brain = api.safe_getattr(brain, "UID")
    >>> uid_obj = api.safe_getattr(client, "UID")

    >>> uid_brain == uid_obj
    True

    >>> api.safe_getattr(brain, "review_state")
    'active'

    >>> api.safe_getattr(brain, "NONEXISTING")
    Traceback (most recent call last):
    [...]
    APIError: Attribute 'NONEXISTING' not found.

    >>> api.safe_getattr(brain, "NONEXISTING", "")
    ''

Getting the Portal Catalog
--------------------------

This tool is needed so often, that this function just returns it::

    >>> api.get_portal_catalog()
    <CatalogTool at /plone/portal_catalog>


Getting the Review History of an Object
---------------------------------------

The review history gives information about the objects' workflow changes::

    >>> review_history = api.get_review_history(client)
    >>> sorted(review_history[0].items())
    [('action', None), ('actor', 'test_user_1_'), ('comments', ''), ('review_state', 'active'), ('time', DateTime('...'))]


Getting the Revision History of an Object
-----------------------------------------

The review history gives information about the objects' workflow changes::

    >>> revision_history = api.get_revision_history(client)
    >>> sorted(revision_history[0])
    ['action', 'actor', 'actor_home', 'actorid', 'comments', 'review_state', 'state_title', 'time', 'transition_title', 'type']
    >>> revision_history[0]["transition_title"]
    u'Create'


Getting the assigned Workflows of an Object
-------------------------------------------

This function returns all assigned workflows for a given object::

    >>> api.get_workflows_for(bika_setup)
    ('senaite_setup_workflow',)

    >>> api.get_workflows_for(client)
    ('senaite_client_workflow',)

This function also supports the portal_type as parameter::

    >>> api.get_workflows_for(api.get_portal_type(client))
    ('senaite_client_workflow',)


Getting the Workflow Status of an Object
----------------------------------------

This function returns the state of a given object::

    >>> api.get_workflow_status_of(client)
    'active'

It is also able to return the state from a brain without waking it up::

    >>> api.get_workflow_status_of(brain)
    'active'

It is also capable to get the state of another state variable::

    >>> api.get_workflow_status_of(client, "review_state")
    'active'

Deactivate the client::

    >>> api.do_transition_for(client, "deactivate")
    <Client at /plone/clients/client-1>

    >>> api.get_workflow_status_of(client)
    'inactive'

Reactivate the client::

    >>> api.do_transition_for(client, "activate")
    <Client at /plone/clients/client-1>

    >>> api.get_workflow_status_of(client)
    'active'


Getting the available transitions for an object
-----------------------------------------------

This function returns all possible transitions from all workflows in the
object's workflow chain.

Let's create a Batch. It should allow us to invoke two different transitions:
'close' and 'cancel':

    >>> batch1 = api.create(portal.batches, "Batch", title="Test Batch")
    >>> transitions = api.get_transitions_for(batch1)
    >>> len(transitions)
    2

The transitions are returned as a list of dictionaries. Since we cannot rely on
the order of dictionary keys, we will have to satisfy ourselves here with
checking that the two expected transitions are present in the return value::

    >>> 'Close' in [t['title'] for t in transitions]
    True
    >>> 'Cancel' in [t['title'] for t in transitions]
    True


Getting the creation date of an object
--------------------------------------

This function returns the creation date of a given object::

    >>> created = api.get_creation_date(client)
    >>> created
    DateTime('...')


Getting the modification date of an object
------------------------------------------

This function returns the modification date of a given object::

    >>> modified = api.get_modification_date(client)
    >>> modified
    DateTime('...')


Getting the review state of an object
-------------------------------------

This function returns the review state of a given object::

    >>> review_state = api.get_review_status(client)
    >>> review_state
    'active'

It should also work for catalog brains::

    >>> portal_catalog = api.get_tool("portal_catalog")
    >>> results = portal_catalog({"portal_type": "Client", "UID": api.get_uid(client)})
    >>> len(results)
    1
    >>> api.get_review_status(results[0]) == review_state
    True


Getting the registered Catalogs of an Object
--------------------------------------------

This function returns a list of all registered catalogs within the
`archetype_tool` for a given portal_type or object::

    >>> api.get_catalogs_for(client)
    [...]

It also supports the `portal_type` as a parameter::

    >>> api.get_catalogs_for("Analysis")
    [...]


Transitioning an Object
-----------------------

This function performs a workflow transition and returns the object::

    >>> client = api.do_transition_for(client, "deactivate")
    >>> api.is_active(client)
    False

    >>> client = api.do_transition_for(client, "activate")
    >>> api.is_active(client)
    True


Getting inactive/cancellation state of different workflows
----------------------------------------------------------

There are two workflows allowing an object to be set inactive.  We provide
the is_active function to return False if an item is set inactive with either
of these workflows.

In the search() test above, the is_active function's handling of brain states
is tested.  Here, I just want to test if object states are handled correctly.

For setup types, we use senaite_deactivable_type_workflow::

    >>> method1 = api.create(portal.methods, "Method", title="Test Method")
    >>> api.is_active(method1)
    True
    >>> method1 = api.do_transition_for(method1, 'deactivate')
    >>> api.is_active(method1)
    False

For transactional types, senaite_cancellable_type_workflow is used::

    >>> maintenance_task = api.create(instrument1, "InstrumentMaintenanceTask", title="Maintenance Task for Instrument 1")
    >>> api.is_active(maintenance_task)
    True
    >>> maintenance_task = api.do_transition_for(maintenance_task, "cancel")
    >>> api.is_active(maintenance_task)
    False

But there are custom workflows that can also provide `cancel` transition, like
`senaite_batch_workflow`, to which `Batch` type is bound:

    >>> batch1 = api.create(portal.batches, "Batch", title="Test Batch")
    >>> api.is_active(batch1)
    True
    >>> batch1 = api.do_transition_for(batch1, 'cancel')
    >>> api.is_active(batch1)
    False


Getting the granted Roles for a certain Permission on an Object
---------------------------------------------------------------

This function returns a list of Roles, which are granted the given Permission
for the passed in object::

    >>> api.get_roles_for_permission("Modify portal content", portal)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> api.get_roles_for_permission("Modify portal content", bika_setup)
    ['LabClerk', 'LabManager', 'Manager']



Checking if an Object is Versionable
------------------------------------

Some contents in SENAITE LIMS support versioning. This function checks this for you.

Instruments are not versionable::

    >>> api.is_versionable(instrument1)
    False

Analysisservices are versionable::

    >>> analysisservices = bika_setup.bika_analysisservices
    >>> analysisservice1 = api.create(analysisservices, "AnalysisService", title="AnalysisService-1")
    >>> analysisservice2 = api.create(analysisservices, "AnalysisService", title="AnalysisService-2")
    >>> analysisservice3 = api.create(analysisservices, "AnalysisService", title="AnalysisService-3")

    >>> api.is_versionable(analysisservice1)
    True


Getting the Version of an Object
--------------------------------

This function returns the version as an integer::

    >>> api.get_version(analysisservice1)
    0

Calling `processForm` bumps the version::

    >>> analysisservice1.processForm()
    >>> api.get_version(analysisservice1)
    1


Getting a Browser View
----------------------

Getting a browser view is a common task in SENAITE LIMS::

    >>> api.get_view("plone")
    <Products.Five.metaclass.Plone object at 0x...>

    >>> api.get_view("workflow_action")
    <Products.Five.metaclass.WorkflowActionHandler object at 0x...>


Getting the Request
-------------------

This function will return the global request object::

    >>> api.get_request()
    <HTTPRequest, URL=http://nohost>


Getting a Group
---------------

Users in SENAITE LIMS are managed in groups. A common group is the `Clients` group,
where all users of client contacts are grouped.
This function gives easy access and is also idempotent::

    >>> clients_group = api.get_group("Clients")
    >>> clients_group
    <GroupData at /plone/portal_groupdata/Clients used for /plone/acl_users/source_groups>

    >>> api.get_group(clients_group)
    <GroupData at /plone/portal_groupdata/Clients used for /plone/acl_users/source_groups>

Non-existing groups are not found::

    >>> api.get_group("NonExistingGroup")


Getting a User
--------------

Users can be fetched by their user id. The function is idempotent and handles
user objects as well::

    >>> from plone.app.testing import TEST_USER_ID
    >>> user = api.get_user(TEST_USER_ID)
    >>> user
    <MemberData at /plone/portal_memberdata/test_user_1_ used for /plone/acl_users>

    >>> api.get_user(api.get_user(TEST_USER_ID))
    <MemberData at /plone/portal_memberdata/test_user_1_ used for /plone/acl_users>

Non-existing users are not found::

    >>> api.get_user("NonExistingUser")


Getting User Properties
-----------------------

User properties, like the email or full name, are stored as user properties.
This means that they are not on the user object. This function retrieves these
properties for you::

    >>> properties = api.get_user_properties(TEST_USER_ID)
    >>> sorted(properties.items())
    [('description', ''), ('email', ''), ('error_log_update', 0.0), ('ext_editor', False), ...]

    >>> sorted(api.get_user_properties(user).items())
    [('description', ''), ('email', ''), ('error_log_update', 0.0), ('ext_editor', False), ...]

An empty property dict is returned if no user could be found::

    >>> api.get_user_properties("NonExistingUser")
    {}

    >>> api.get_user_properties(None)
    {}


Getting Users by their Roles
----------------------------

    >>> from operator import methodcaller

Roles in SENAITE LIMS are basically a name for one or more permissions. For
example, a `LabManager` describes a role which is granted the most permissions.

So first I'll add some users with some different roles:

    >>> for user in [{'username': 'labmanager_1', 'roles': ['LabManager']},
    ...              {'username': 'labmanager_2', 'roles': ['LabManager']},
    ...              {'username': 'sampler_1', 'roles': ['Sampler']},
    ...              {'username': 'client_1', 'roles': ['Client']}]:
    ...    member = portal.portal_registration.addMember(
    ...        user['username'], user['username'],
    ...        properties={'username': user['username'],
    ...                    'email': user['username'] + "@example.com",
    ...                    'fullname': user['username']})
    ...    setRoles(portal, user['username'], user['roles'])
    ...    # If user is a LabManager, add Owner local role on clients folder
    ...    # TODO ask @ramonski, is this still required?
    ...    if 'LabManager' in user['roles']:
    ...        portal.clients.manage_setLocalRoles(user['username'], ['Owner'])


To see which users are granted a certain role, you can use this function::

    >>> labmanagers = api.get_users_by_roles(["LabManager"])
    >>> sorted(labmanagers, key=methodcaller('getId'))
    [<PloneUser 'labmanager_1'>, <PloneUser 'labmanager_2'>]

A single value can also be passed into this function::

    >>> sorted(api.get_users_by_roles("Sampler"), key=methodcaller('getId'))
    [<PloneUser 'sampler_1'>]


Getting the Current User
------------------------

Getting the current logged in user::

    >>> api.get_current_user()
    <MemberData at /plone/portal_memberdata/test_user_1_ used for /plone/acl_users>


Getting the Contact associated to a Plone user
----------------------------------------------

Getting a Plone user previously registered with no contact assigned:

    >>> user = api.get_user('labmanager_1')
    >>> contact = api.get_user_contact(user)
    >>> contact is None
    True

Assign a new contact to this user:

    >>> labcontacts = bika_setup.bika_labcontacts
    >>> labcontact = api.create(labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> labcontact.setUser(user)
    True

And get the contact associated to the user:

    >>> api.get_user_contact(user)
    <LabContact at /plone/bika_setup/bika_labcontacts/labcontact-1>

As well as if we specify only `LabContact` type:

    >>> api.get_user_contact(user, ['LabContact'])
    <LabContact at /plone/bika_setup/bika_labcontacts/labcontact-1>

But fails if we specify only `Contact` type:

    >>> nuser = api.get_user_contact(user, ['Contact'])
    >>> nuser is None
    True


Getting the Contact Client
--------------------------

Getting the current client the current user belongs to::

    >>> api.get_current_client() is None
    True

And still fails if we use a user that is not associated to a client::

    >>> api.get_user_client(user) is None
    True

    >>> api.get_user_client(labcontact) is None
    True

Try now with a valid contact::

    >>> client_user = api.get_user('client_1')
    >>> contact1 = api.create(client, "Contact", Firstname="Lost", Lastname="Nomad")
    >>> contact1.setUser(client_user)
    True

    >>> api.get_user_client(contact1)
    <Client at /plone/clients/client-1>

    >>> api.get_user_client(client_user)
    <Client at /plone/clients/client-1>


Creating a Cache Key
--------------------

This function creates a good cache key for a generic object or brain::

    >>> key1 = api.get_cache_key(client)
    >>> key1
    'Client-client-1-...'

This can be also done for a catalog result brain::

    >>> portal_catalog = api.get_tool("portal_catalog")
    >>> brains = portal_catalog({"portal_type": "Client", "UID": api.get_uid(client)})
    >>> key2 = api.get_cache_key(brains[0])
    >>> key2
    'Client-client-1-...'

The two keys should be equal::

    >>> key1 == key2
    True

The key should change when the object get modified::

    >>> from zope.lifecycleevent import modified
    >>> client.setClientID("TESTCLIENT")
    >>> modified(client)
    >>> portal.aq_parent._p_jar.sync()
    >>> key3 = api.get_cache_key(client)
    >>> key3 != key1
    True

.. important:: Workflow changes do not change the modification date!
A custom event subscriber will update it therefore.

A workflow transition should also change the cache key::

    >>> _ = api.do_transition_for(client, transition="deactivate")
    >>> api.is_active(client)
    False
    >>> key4 = api.get_cache_key(client)
    >>> key4 != key3
    True


SENAITE Cache Key decorator
---------------------------

This decorator can be used for `plone.memoize` cache decorators in classes.
The decorator expects that the first argument is the class instance (`self`) and
the second argument a brain or object::

    >>> from plone.memoize.volatile import cache

    >>> class SENAITEClass(object):
    ...     @cache(api.bika_cache_key_decorator)
    ...     def get_very_expensive_calculation(self, obj):
    ...         print "very expensive calculation"
    ...         return "calculation result"

Calling the (expensive) method of the class does the calculation just once::

    >>> instance = SENAITEClass()
    >>> instance.get_very_expensive_calculation(client)
    very expensive calculation
    'calculation result'
    >>> instance.get_very_expensive_calculation(client)
    'calculation result'

The decorator can also handle brains::

    >>> instance = SENAITEClass()
    >>> portal_catalog = api.get_tool("portal_catalog")
    >>> brain = portal_catalog(portal_type="Client")[0]
    >>> instance.get_very_expensive_calculation(brain)
    very expensive calculation
    'calculation result'
    >>> instance.get_very_expensive_calculation(brain)
    'calculation result'


ID Normalizer
-------------

Normalizes a string to be usable as a system ID:

    >>> api.normalize_id("My new ID")
    'my-new-id'

    >>> api.normalize_id("Really/Weird:Name;")
    'really-weird-name'

    >>> api.normalize_id(None)
    Traceback (most recent call last):
    [...]
    APIError: Type of argument must be string, found '<type 'NoneType'>'


File Normalizer
---------------

Normalizes a string to be usable as a file name:

    >>> api.normalize_filename("My new ID")
    'My new ID'

    >>> api.normalize_filename("Really/Weird:Name;")
    'Really-Weird-Name'

    >>> api.normalize_filename(None)
    Traceback (most recent call last):
    [...]
    APIError: Type of argument must be string, found '<type 'NoneType'>'


Check if an UID is valid
------------------------

Checks if an UID is a valid 23 alphanumeric uid:

    >>> api.is_uid("ajw2uw9")
    False

    >>> api.is_uid(None)
    False

    >>> api.is_uid("")
    False

    >>> api.is_uid('0e1dfc3d10d747bf999948a071bc161e')
    True

Per convention we assume "0" is the uid for portal object (PloneSite):

    >>> api.is_uid("0")
    True

Checks if an UID is a valid 23 alphanumeric uid and with a brain:

    >>> api.is_uid("ajw2uw9", validate=True)
    False

    >>> api.is_uid(None, validate=True)
    False

    >>> api.is_uid("", validate=True)
    False

    >>> api.is_uid('0e1dfc3d10d747bf999948a071bc161e', validate=True)
    False

    >>> api.is_uid("0", validate=True)
    True

    >>> asfolder = self.portal.bika_setup.bika_analysisservices
    >>> serv = api.create(asfolder, "AnalysisService", title="AS test")
    >>> serv.setKeyword("as_test")
    >>> uid = serv.UID()
    >>> api.is_uid(uid, validate=True)
    True


Check if a Date is valid
------------------------

Do some imports first:

    >>> from datetime import datetime
    >>> from DateTime import DateTime

Checks if a DateTime is valid:

    >>> now = DateTime()
    >>> api.is_date(now)
    True

    >>> now = datetime.now()
    >>> api.is_date(now)
    True

    >>> now = DateTime(now)
    >>> api.is_date(now)
    True

    >>> api.is_date(None)
    False

    >>> api.is_date('2018-04-23')
    False


Try conversions to Date
-----------------------

Try to convert to DateTime:

    >>> now = DateTime()
    >>> zpdt = api.to_date(now)
    >>> zpdt.ISO8601() == now.ISO8601()
    True

    >>> now = datetime.now()
    >>> zpdt = api.to_date(now)
    >>> pydt = zpdt.asdatetime()

Note that here, for the comparison between dates, we convert DateTime to python
datetime, cause DateTime.strftime() is broken for timezones (always looks at
system time zone, ignores the timezone and offset of the DateTime instance
itself):

    >>> pydt.strftime('%Y-%m-%dT%H:%M:%S') == now.strftime('%Y-%m-%dT%H:%M:%S')
    True

Try the same, but with utcnow() instead:

    >>> now = datetime.utcnow()
    >>> zpdt = api.to_date(now)
    >>> pydt = zpdt.asdatetime()
    >>> pydt.strftime('%Y-%m-%dT%H:%M:%S') == now.strftime('%Y-%m-%dT%H:%M:%S')
    True

Now we convert just a string formatted date:

    >>> strd = "2018-12-01 17:50:34"
    >>> zpdt = api.to_date(strd)
    >>> zpdt.ISO8601()
    '2018-12-01T17:50:34'

Now we convert just a string formatted date, but with timezone:

    >>> strd = "2018-12-01 17:50:34 GMT+1"
    >>> zpdt = api.to_date(strd)
    >>> zpdt.ISO8601()
    '2018-12-01T17:50:34+01:00'

We also check a bad date here (note the month is 13):

    >>> strd = "2018-13-01 17:50:34"
    >>> zpdt = api.to_date(strd)
    >>> api.is_date(zpdt)
    False

And with European format:

    >>> strd = "01.12.2018 17:50:34"
    >>> zpdt = api.to_date(strd)
    >>> zpdt.ISO8601()
    '2018-12-01T17:50:34'

    >>> zpdt = api.to_date(None)
    >>> zpdt is None
    True

Use a string formatted date as fallback:

    >>> strd = "2018-13-01 17:50:34"
    >>> default_date = "2018-01-01 19:30:30"
    >>> zpdt = api.to_date(strd, default_date)
    >>> zpdt.ISO8601()
    '2018-01-01T19:30:30'

Use a DateTime object as fallback:

    >>> strd = "2018-13-01 17:50:34"
    >>> default_date = "2018-01-01 19:30:30"
    >>> default_date = api.to_date(default_date)
    >>> zpdt = api.to_date(strd, default_date)
    >>> zpdt.ISO8601() == default_date.ISO8601()
    True

Use a datetime object as fallback:

    >>> strd = "2018-13-01 17:50:34"
    >>> default_date = datetime.now()
    >>> zpdt = api.to_date(strd, default_date)
    >>> dzpdt = api.to_date(default_date)
    >>> zpdt.ISO8601() == dzpdt.ISO8601()
    True

Use a non-conversionable value as fallback:

    >>> strd = "2018-13-01 17:50:34"
    >>> default_date = "something wrong here"
    >>> zpdt = api.to_date(strd, default_date)
    >>> zpdt is None
    True


Check if floatable
------------------

    >>> api.is_floatable(None)
    False

    >>> api.is_floatable("")
    False

    >>> api.is_floatable("31")
    True

    >>> api.is_floatable("31.23")
    True

    >>> api.is_floatable("-13")
    True

    >>> api.is_floatable("12,35")
    False


Convert to a float number
-------------------------

    >>> api.to_float("2")
    2.0

    >>> api.to_float("2.234")
    2.234

With default fallback:

    >>> api.to_float(None, 2)
    2.0

    >>> api.to_float(None, "2")
    2.0

    >>> api.to_float("", 2)
    2.0

    >>> api.to_float("", "2")
    2.0

    >>> api.to_float(2.1, 2)
    2.1

    >>> api.to_float("2.1", 2)
    2.1

    >>> api.to_float("2.1", "2")
    2.1


Convert to an int number
------------------------

    >>> api.to_int(2)
    2

    >>> api.to_int("2")
    2

    >>> api.to_int(2.1)
    2

    >>> api.to_int("2.1")
    2

With default fallback:

    >>> api.to_int(None, 2)
    2

    >>> api.to_int(None, "2")
    2

    >>> api.to_int("", 2)
    2

    >>> api.to_int("2", 0)
    2

    >>> api.to_int(2, 0)
    2

    >>> api.to_int("as", None) is None
    True

    >>> api.to_int("as", "2")
    2


Convert to minutes
------------------

    >>> api.to_minutes(hours=1)
    60

    >>> api.to_minutes(hours=1.5, minutes=30)
    120

    >>> api.to_minutes(hours=0, minutes=0, seconds=0)
    0

    >>> api.to_minutes(minutes=120)
    120

    >>> api.to_minutes(hours="1", minutes="120", seconds="120")
    182

    >>> api.to_minutes(days=3)
    4320

    >>> api.to_minutes(minutes=122.4567)
    122

    >>> api.to_minutes(minutes=122.4567, seconds=6)
    123

    >>> api.to_minutes(minutes=122.4567, seconds=6, round_to_int=False)
    122.55669999999999


Convert to dhm format
---------------------

    >>> api.to_dhm_format(hours=1)
    '1h'

    >>> api.to_dhm_format(hours=1.5, minutes=30)
    '2h'

    >>> api.to_dhm_format(hours=0, minutes=0, seconds=0)
    ''

    >>> api.to_dhm_format(minutes=120)
    '2h'

    >>> api.to_dhm_format(hours="1", minutes="120", seconds="120")
    '3h 2m'

    >>> api.to_dhm_format(days=3)
    '3d'

    >>> api.to_dhm_format(days=3, minutes=140)
    '3d 2h 20m'

    >>> api.to_dhm_format(days=3, minutes=20)
    '3d 0h 20m'

    >>> api.to_dhm_format(minutes=122.4567)
    '2h 2m'

    >>> api.to_dhm_format(minutes=122.4567, seconds=6)
    '2h 3m'


Get a registry record
---------------------

Fetch a value of a registry record::

    >>> key = "Products.CMFPlone.i18nl10n.override_dateformat.Enabled"
    >>> api.get_registry_record(key)
    False

If the record is not found, the default is returned::

    >>> key = "non.existing.key"
    >>> api.get_registry_record(key, default="NX_KEY")
    'NX_KEY'


Create a display list
---------------------

Static display lists, can look up on either side of the dict, and get them in
sorted order. They are used in selection widgets.

The function can handle a list of key->value pairs:

    >>> pairs = [["a", "A"], ["b", "B"]]
    >>> api.to_display_list(pairs)
    <DisplayList [('', ''), ('a', 'A'), ('b', 'B')] at ...>

It can also handle a single pair:

    >>> pairs = ["z", "Z"]
    >>> api.to_display_list(pairs)
    <DisplayList [('', ''), ('z', 'Z')] at ...>

It can also handle a single string:

    >>> api.to_display_list("x")
    <DisplayList [('', ''), ('x', 'x')] at ...>

It can be sorted either by key or by value:

    >>> pairs = [["b", 10], ["a", 100]]
    >>> api.to_display_list(pairs)
    <DisplayList [('', ''), ('a', 100), ('b', 10)] at ...>

    >>> api.to_display_list(pairs, sort_by="value")
    <DisplayList [('b', 10), ('a', 100), ('', '')] at ...>


Converting a text to HTML
-------------------------

This function converts newline (`\n`) escape sequences in plain text to `<br/>`
tags for HTML rendering.

The function can handle plain texts:

    >>> text = "First\r\nSecond\r\nThird"
    >>> api.text_to_html(text)
    '<p>First\r<br/>Second\r<br/>Third</p>'

Unicodes texts work as well:

    >>> text = u"Ä\r\nÖ\r\nÜ"
    >>> api.text_to_html(text)
    '<p>\xc3\x83\xc2\x84\r<br/>\xc3\x83\xc2\x96\r<br/>\xc3\x83\xc2\x9c</p>'

The outer `<p>` wrap can be also omitted:

    >>> text = "One\r\nTwo"
    >>> api.text_to_html(text, wrap=None)
    'One\r<br/>Two'

Or changed to another tag:

    >>> text = "One\r\nTwo"
    >>> api.text_to_html(text, wrap="div")
    '<div>One\r<br/>Two</div>'

Empty strings are returned unchanged:

    >>> text = ""
    >>> api.text_to_html(text, wrap="div")
    ''
