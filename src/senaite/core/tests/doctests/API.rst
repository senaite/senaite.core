SENAITE LIMS API
----------------

The SENAITE LIMS API provides single functions for single purposes.
This Test builds completely on the API without any further imports needed.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API

API
---

The purpose of this API is to help coders to follow the DRY principle (Don't
Repeat Yourself). It also ensures that the most effective and efficient method is
used to achieve a task.

Import it first::

    >>> from bika.lims import api


Setup the test user
...................

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

    >>> from senaite.app.supermodel import SuperModel


Getting the Portal
..................

The Portal is the SENAITE LIMS root object::

    >>> portal = api.get_portal()
    >>> portal
    <PloneSite at /plone>


Getting the SENAITE Setup object
................................

The Setup object gives access to all of the SENAITE configuration settings::

    >>> setup = api.get_setup()
    >>> setup
    <BikaSetup at /plone/bika_setup>

    >>> bika_setup = api.get_bika_setup()
    >>> setup
    <BikaSetup at /plone/bika_setup>

    >>> setup == bika_setup
    True


Since version 2.3.0 we provide a Dexterity based setup folder to hold configuration values:


    >>> senaite_setup = api.get_senaite_setup()
    >>> senaite_setup
    <Setup at /plone/setup>


Creating new Content
....................

Creating new contents in SENAITE LIMS requires some special knowledge.
This function helps to do it right and creates a content for you.

Here we create a new `Client` in the `plone/clients` folder::

    >>> client = api.create(portal.clients, "Client", title="Test Client")
    >>> client
    <Client at /plone/clients/client-1>

    >>> client.Title()
    'Test Client'

Created objects are properly indexed::

    >>> services = self.portal.bika_setup.bika_analysisservices
    >>> service = api.create(services, "AnalysisService",
    ...                      title="Dummy service", Keyword="DUM")
    >>> uid = api.get_uid(service)
    >>> catalog = api.get_tool("senaite_catalog_setup")
    >>> brains = catalog(portal_type="AnalysisService", UID=uid)
    >>> brains[0].getKeyword
    'DUM'


Editing Content
...............

This function helps to edit a given content.

Here we update the `Client` we created earlier, an AT::

    >>> api.edit(client, AccountNumber="12343567890", BankName="BTC Bank")
    >>> client.getAccountNumber()
    '12343567890'

    >>> client.getBankName()
    'BTC Bank'

It also works for DX content types::

    >>> api.edit(senaite_setup, site_logo_css="my-test-logo")
    >>> senaite_setup.getSiteLogoCSS()
    'my-test-logo'

The field need to be writeable::

    >>> field = client.getField("BankName")
    >>> field.readonly = True
    >>> api.edit(client, BankName="Lydian Lion Coins Bank")
    Traceback (most recent call last):
    [...]
    ValueError: Field 'BankName' is readonly

    >>> client.getBankName()
    'BTC Bank'

    >>> field.readonly = False
    >>> api.edit(client, BankName="Lydian Lion Coins Bank")
    >>> client.getBankName()
    'Lydian Lion Coins Bank'

And user need to have enough permissions to change the value as well::

    >>> field.write_permission = "Delete objects"
    >>> api.edit(client, BankName="Electrum Coins")
    Traceback (most recent call last):
    [...]
    Unauthorized: Field 'BankName' is not writeable

    >>> client.getBankName()
    'Lydian Lion Coins Bank'

Unless we manually force to bypass the permissions check::

    >>> api.edit(client, check_permissions=False, BankName="Electrum Coins")
    >>> client.getBankName()
    'Electrum Coins'

Restore permission::

    >>> field.write_permission = "Modify Portal Content"


Getting a Tool
..............

There are many ways to get a tool in SENAITE LIMS / Plone. This function
centralizes this functionality and makes it painless::

    >>> api.get_tool("senaite_catalog_setup")
    <SetupCatalog at /plone/senaite_catalog_setup>

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

When default param is specified, the system returns the tool if the parameter
is a string:

    >>> api.get_tool("NotExistingTool", default="senaite_catalog_setup")
    <SetupCatalog at /plone/senaite_catalog_setup>

but returns the default value otherwise:

    >>> api.get_tool("NotExistingTool", default=None) is None
    True

    >>> catalog_setup = api.get_tool("senaite_catalog_setup")
    >>> api.get_tool("NotExistingTool", default=catalog_setup)
    <SetupCatalog at /plone/senaite_catalog_setup>


Getting an Object
.................

Getting the object from a catalog brain is a common task.

This function provides an unified interface to portal objects **and** brains.
Furthermore it is idempotent, so it can be called multiple times in a row.

We will demonstrate the usage on the client object we created above::

    >>> api.get_object(client)
    <Client at /plone/clients/client-1>

    >>> api.get_object(api.get_object(client))
    <Client at /plone/clients/client-1>

Now we show it with catalog results::

    >>> brains = api.search({"portal_type": "Client"})
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

And also accepts `SuperModel` objects:

    >>> api.get_object(SuperModel(brain))
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

    >>> api.is_object(SuperModel(client))
    True

    >>> api.is_object(None)
    False

    >>> api.is_object(object())
    False


Checking if an Object is the Portal
...................................

Sometimes it can be handy to check if the current object is the portal::

    >>> api.is_portal(portal)
    True

    >>> api.is_portal(client)
    False

    >>> api.is_portal(object())
    False


Checking if an Object is a Catalog Brain
........................................

Knowing if we have an object or a brain can be handy. This function checks this for you::

    >>> api.is_brain(brain)
    True

    >>> api.is_brain(api.get_object(brain))
    False

    >>> api.is_brain(object())
    False


Checking if an Object is a Dexterity Content
............................................

This function checks if an object is a `Dexterity` content type::

    >>> api.is_dexterity_content(client)
    False

    >>> api.is_dexterity_content(portal)
    False

It is also possible to check by portal type::

    >>> api.is_dx_type("InterpretationTemplate")
    True

    >>> api.is_dx_type("Client")
    False


Checking if an Object is an AT Content
......................................

This function checks if an object is an `Archetypes` content type::

    >>> api.is_at_content(client)
    True

    >>> api.is_at_content(portal)
    False

    >>> api.is_at_content(object())
    False


It is also possible to check by portal type::

    >>> api.is_at_type("Client")
    True

    >>> api.is_at_type("InterpretationTemplate")
    False


Getting the Schema of a Content
...............................

The schema contains the fields of a content object. Getting the schema is a
common task, but differs between `ATContentType` based objects and `Dexterity`
based objects. This function brings it under one umbrella::

    >>> schema = api.get_schema(client)
    >>> schema
    <Products.Archetypes.Schema.Schema object at 0x...>

Catalog brains are also supported::

    >>> api.get_schema(brain)
    <Products.Archetypes.Schema.Schema object at 0x...>



Getting the behaviors of a type
...............................

Dexterity contents might extend schema fields over a behavior.
This function shows the current active behaviors:

    >>> api.get_behaviors("SampleContainer")
    (...)

It is possible to enable behaviors dynamically:

    >>> "plone.basic" in api.get_behaviors("SampleContainer")
    False

    >>> api.enable_behavior("SampleContainer", "plone.basic")

    >>> "plone.basic" in api.get_behaviors("SampleContainer")
    True

And remove it again:

    >>> api.disable_behavior("SampleContainer", "plone.basic")

    >>> "plone.basic" in api.get_behaviors("SampleContainer")
    False


Getting the Fields of a Content
...............................

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
...........................

Getting the ID is a common task in SENAITE LIMS.
This function takes care that catalog brains are not woken up for this task::

    >>> api.get_id(portal)
    'plone'

    >>> api.get_id(client)
    'client-1'

    >>> api.get_id(brain)
    'client-1'


Getting the Title of a Content
..............................

Getting the Title is a common task in SENAITE LIMS.
This function takes care that catalog brains are not woken up for this task::

    >>> api.get_title(portal)
    'SENAITE LIMS'

    >>> api.get_title(client)
    'Test Client'

    >>> api.get_title(brain)
    'Test Client'


Getting the Description of a Content
....................................

Getting the Description is a common task in SENAITE LIMS.
This function takes care that catalog brains are not woken up for this task::

    >>> api.get_description(portal)
    ''

    >>> api.get_description(client)
    ''

    >>> api.get_description(brain)
    ''


Getting the UID of a Content
............................

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
............................

Getting the URL is a common task in SENAITE LIMS.
This function takes care that catalog brains are not woken up for this task::

    >>> api.get_url(portal)
    'http://nohost/plone'

    >>> api.get_url(client)
    'http://nohost/plone/clients/client-1'

    >>> api.get_url(brain)
    'http://nohost/plone/clients/client-1'


Getting the Icon of a Content
.............................

    >>> api.get_icon(client)
    '<img width="16" height="16" src="http://nohost/plone/senaite_theme/icon/client" title="Test Client" />'

    >>> api.get_icon(brain)
    '<img width="16" height="16" src="http://nohost/plone/senaite_theme/icon/client" title="Test Client" />'

It works for portal types that resolve to DynamicViewTypeInformation (Archetypes):

    >>> api.get_icon("Client")
    '<img width="16" height="16" src="http://nohost/plone/senaite_theme/icon/client" title="Client" />'

And also for portal types that resolve to DexterityFTI (Dexterity):

    >>> api.get_icon("SampleContainer")
    '<img width="16" height="16" src="http://nohost/plone/senaite_theme/icon/container" title="Sample Container" />'

But fails when is not possible to resolve the FTI:

    >>> api.get_icon("NonExistingType")
    Traceback (most recent call last):
    [...]
    APIError: No type info for 'NonExistingType'

    >>> api.get_icon(object)
    Traceback (most recent call last):
    [...]
    APIError: No type info for <type 'object'>

The function can also be used to simplyh retrieve the url:

    >>> api.get_icon(client, html_tag=False)
    'http://nohost/plone/senaite_theme/icon/client'

    >>> api.get_icon(client, html_tag=False)
    'http://nohost/plone/senaite_theme/icon/client'

    >>> api.get_icon("Client", html_tag=False)
    'http://nohost/plone/senaite_theme/icon/client'

    >>> api.get_icon("SampleContainer", html_tag=False)
    'http://nohost/plone/senaite_theme/icon/container'

    >>> api.get_icon("NonExistingType", html_tag=False)
    Traceback (most recent call last):
    [...]
    APIError: No type info for 'NonExistingType'


Getting a catalog brain by UID
..............................

This function finds a catalog brain by its uinique ID (UID)::

    >>> api.get_brain_by_uid(api.get_uid(client))
    <Products.Archetypes.UIDCatalog.plugbrains object at ...>


Getting an object by UID
........................

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
.........................

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
......................................

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
.............................................

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
.........................

This function returns the parent object::

    >>> api.get_parent(client)
    <ClientFolder at /plone/clients>

Brains are also supported::

    >>> api.get_parent(brain)
    <ClientFolder at /plone/clients>

However, this function goes only up to the portal object::

    >>> api.get_parent(portal)
    <PloneSite at /plone>

Like with the other functions, only portal objects are supported::

    >>> api.get_parent(object())
    Traceback (most recent call last):
    [...]
    APIError: <object object at 0x...> is not supported.


Searching Objects
.................

Searching in SENAITE LIMS requires knowledge in which catalog the object is indexed.
This function unifies all SENAITE LIMS catalog to a single search interface::

    >>> results = api.search({'portal_type': 'Client'})
    >>> results
    [<Products.ZCatalog.Catalog.mybrains object at 0x...>]

Now we create some objects which are located in the `senaite_catalog_setup`::

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

Catalog queries w/o any `portal_type`, default to the `uid_catalog`::

    >>> analysiscategories = bika_setup.bika_analysiscategories
    >>> analysiscategory1 = api.create(analysiscategories, "AnalysisCategory", title="AC-1")
    >>> analysiscategory2 = api.create(analysiscategories, "AnalysisCategory", title="AC-2")
    >>> analysiscategory3 = api.create(analysiscategories, "AnalysisCategory", title="AC-3")

    >>> results = api.search({"id": "analysiscategory-1"})
    >>> len(results)
    1
    >>> res = results[0]
    >>> res.aq_parent
    <UIDCatalog at /plone/uid_catalog>

Would we add the `portal_type`, the search function would ask the
`archetype_tool` for the right catalog, and it would return a result::

    >>> results = api.search({"portal_type": "AnalysisCategory", "id": "analysiscategory-1"})
    >>> len(results)
    1

We could also explicitly define a catalog to achieve the same::

    >>> results = api.search({"id": "analysiscategory-1"}, catalog="senaite_catalog_setup")
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
...............................

SENAITE LIMS uses **multiple catalogs** for different content types.
This function returns a list of registered catalogs for a brain, object, UID or portal_type.

Get the mapped catalogs for an AT content type:

    >>> api.get_catalogs_for(client)
    [<ClientCatalog at /plone/senaite_catalog_client>]

Passing in the portal_type should return the same:

    >>> api.get_catalogs_for(api.get_portal_type(client))
    [<ClientCatalog at /plone/senaite_catalog_client>]

Even if we pass in the UID, we should get the same results:

    >>> api.get_catalogs_for(api.get_uid(client))
    [<ClientCatalog at /plone/senaite_catalog_client>]

Dexterity contents that provide IMulitCatalogBehavior should work as well:

    >>> api.get_catalogs_for(senaite_setup)
    [<CatalogTool at /plone/portal_catalog>]


Getting the FTI for a portal type
.................................

This function provides the dynamic type information for a given portal type:

    >>> api.get_fti("Client")
    <DynamicViewTypeInformation at /plone/portal_types/Client>

    >>> api.get_fti("Label")
    <DexterityFTI at /plone/portal_types/Label>



Getting an Attribute of an Object
.................................

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

Getting the UID Catalog
.......................

This tool is needed so often, that this function just returns it::

    >>> api.get_uid_catalog()
    <UIDCatalog at /plone/uid_catalog>


Getting the Review History of an Object
.......................................

The review history gives information about the objects' workflow changes::

    >>> review_history = api.get_review_history(client)
    >>> sorted(review_history[0].items())
    [('action', None), ('actor', 'test_user_1_'), ('comments', ''), ('review_state', 'active'), ('time', DateTime('...'))]


Getting the Revision History of an Object
.........................................

The review history gives information about the objects' workflow changes::

    >>> revision_history = api.get_revision_history(client)
    >>> sorted(revision_history[0])
    ['action', 'actor', 'actor_home', 'actorid', 'comments', 'review_state', 'state_title', 'time', 'transition_title', 'type']
    >>> revision_history[0]["transition_title"]
    u'Create'


Getting the assigned Workflows of an Object
...........................................

This function returns all assigned workflows for a given object::

    >>> api.get_workflows_for(bika_setup)
    ('senaite_setup_workflow',)

    >>> api.get_workflows_for(client)
    ('senaite_client_workflow',)

This function also supports the portal_type as parameter::

    >>> api.get_workflows_for(api.get_portal_type(client))
    ('senaite_client_workflow',)


Getting the Workflow Status of an Object
........................................

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


Getting the previous Workflow Status of an Object
.................................................


This function gives the last worflow state of an object:

    >>> api.get_workflow_status_of(client)
    'active'

    >>> api.get_previous_worfklow_status_of(client)
    'inactive'

Specific states can be skipped:

    >>> api.get_previous_worfklow_status_of(client, skip=['inactive'])
    'active'

A default value can be set in case no previous state was found:

    >>> api.get_previous_worfklow_status_of(client, skip=['active' ,'inactive'], default='notfound')
    'notfound'


Getting the available transitions for an object
...............................................

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
......................................

This function returns the creation date of a given object::

    >>> created = api.get_creation_date(client)
    >>> created
    DateTime('...')


Getting the modification date of an object
..........................................

This function returns the modification date of a given object::

    >>> modified = api.get_modification_date(client)
    >>> modified
    DateTime('...')


Getting the review state of an object
.....................................

This function returns the review state of a given object::

    >>> review_state = api.get_review_status(client)
    >>> review_state
    'active'

It should also work for catalog brains::

    >>> results = api.search({"portal_type": "Client", "UID": api.get_uid(client)})
    >>> len(results)
    1
    >>> api.get_review_status(results[0]) == review_state
    True


Getting the registered Catalogs of an Object
............................................

This function returns a list of all registered catalogs within the
`archetype_tool` for a given portal_type or object::

    >>> api.get_catalogs_for(client)
    [...]

It also supports the `portal_type` as a parameter::

    >>> api.get_catalogs_for("Analysis")
    [...]


Transitioning an Object
.......................

This function performs a workflow transition and returns the object::

    >>> client = api.do_transition_for(client, "deactivate")
    >>> api.is_active(client)
    False

    >>> client = api.do_transition_for(client, "activate")
    >>> api.is_active(client)
    True


Getting inactive/cancellation state of different workflows
..........................................................

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
...............................................................

This function returns a list of Roles, which are granted the given Permission
for the passed in object::

    >>> api.get_roles_for_permission("Modify portal content", portal)
    ['LabClerk', 'LabManager', 'Manager', 'Owner']

    >>> api.get_roles_for_permission("Modify portal content", bika_setup)
    ['LabClerk', 'LabManager', 'Manager']



Checking if an Object is Versionable
....................................

NOTE: Versioning is outdated!
      This code will be removed as soon as we drop the `HistoryAwareReferenceField`
      reference between Calculation and Analysis.

Instruments are not versionable::

    >>> api.is_versionable(instrument1)
    False

Calculations are versionable::

    >>> calculations = bika_setup.bika_calculations
    >>> calc = api.create(calculations, "Calculation", title="Calculation 1")

    >>> api.is_versionable(calc)
    True


Getting the Version of an Object
................................

This function returns the version as an integer::

    >>> api.get_version(calc)
    0

Calling `processForm` bumps the version::

    >>> calc.processForm()
    >>> api.get_version(calc)
    1


Getting a Browser View
......................

Getting a browser view is a common task in SENAITE LIMS::

    >>> api.get_view("plone")
    <Products.Five.browser.metaconfigure.Plone object at 0x...>


    >>> api.get_view("workflow_action")
    <Products.Five.browser.metaconfigure.WorkflowActionHandler object at 0x...>


Getting the Request
...................

This function will return the global request object::

    >>> api.get_request()
    <HTTPRequest, URL=http://nohost>


Getting a Group
...............

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
..............

Users can be fetched by their user id. The function is idempotent and handles
user objects as well::

    >>> from plone.app.testing import TEST_USER_ID
    >>> user = api.get_user(TEST_USER_ID)
    >>> user
    <Products.PlonePAS.tools.memberdata.MemberData object at 0x...>

    >>> api.get_user(api.get_user(TEST_USER_ID))
    <Products.PlonePAS.tools.memberdata.MemberData object at 0x...>

Non-existing users are not found::

    >>> api.get_user("NonExistingUser")


Getting User Properties
.......................

User properties, like the email or full name, are stored as user properties.
This means that they are not on the user object. This function retrieves these
properties for you::

    >>> properties = api.get_user_properties(TEST_USER_ID)
    >>> props = dict(properties.items())
    >>> "email" in props
    True

    >>> props = dict(api.get_user_properties(user).items())
    >>> "email" in props
    True

An empty property dict is returned if no user could be found::

    >>> api.get_user_properties("NonExistingUser")
    {}

    >>> api.get_user_properties(None)
    {}


Getting Users by their Roles
............................

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
........................

Getting the current logged in user::

    >>> api.get_current_user()
    <Products.PlonePAS.tools.memberdata.MemberData object at 0x...


Getting the Contact associated to a Plone user
..............................................

Getting a Plone user previously registered with no contact assigned:

    >>> user = api.get_user('labmanager_1')
    >>> contact = api.get_user_contact(user)
    >>> contact is None
    True

Assign a new contact to this user:

    >>> labcontacts = bika_setup.bika_labcontacts
    >>> labcontact = api.create(labcontacts, "LabContact", Firstname="Lab", Surname="Manager")
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


Getting the fullname of the user and/or contact
..............................................

Getting the fullname of the contact::

    >>> api.get_user_fullname(labcontact)
    'Lab Manager'

Getting the fullname of the user::

    >>> api.get_user_fullname(user)
    'Lab Manager'

Note that if contact's fullname has priority over user's::

    >>> user.setProperties(fullname="Labby Man")
    >>> api.get_user_fullname(user)
    'Lab Manager'

But returns the user's fullname when not linked to any contact::

    >>> labcontact.unlinkUser()
    True
    >>> api.get_user_fullname(user)
    'Labby Man'

Relink the user again

    >>> labcontact.setUser(user)
    True


Getting the email of the user and/or contact
............................................

Getting the email of the contact::

    >>> labcontact.setEmailAddress("labman@example.com")
    >>> api.get_user_email(labcontact)
    'labman@example.com'

Getting the email of the user::

    >>> api.get_user_email(user)
    'labman@example.com'

Note that contact's email has priority over user's::

    >>> user.setProperties(email="labbyman@example.com")
    >>> api.get_user_email(user)
    'labman@example.com'

But returns the user's email when not linked to any contact::

    >>> labcontact.unlinkUser()
    True
    >>> api.get_user_email(user)
    'labbyman@example.com'

Relink the user again

    >>> labcontact.setUser(user)
    True


Getting the Contact Client
..........................

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

Unset the user again

    >>> contact1.unlinkUser(client_user)
    True


Creating a Cache Key
....................

This function creates a good cache key for a generic object or brain::

    >>> key1 = api.get_cache_key(client)
    >>> key1
    'Client-client-1-...'

NOTE: Function will be deleted in senaite.core 3.0.0


SENAITE Cache Key decorator
...........................

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

    >>> from senaite.core.catalog import CLIENT_CATALOG
    >>> instance = SENAITEClass()
    >>> cat = api.get_tool(CLIENT_CATALOG)
    >>> brain = cat(portal_type="Client")[0]
    >>> instance.get_very_expensive_calculation(brain)
    very expensive calculation
    'calculation result'
    >>> instance.get_very_expensive_calculation(brain)
    'calculation result'

NOTE: Function will be deleted in senaite.core 3.0.0


ID Normalizer
.............

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
...............

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
........................

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
........................

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
.......................

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
..................

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
.........................

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
........................

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


Convert float to string
.......................

Values below zero get converted by the `float` class to the exponential notation, e.g.

    >>> value = "0.000000000123"
    >>> float_value = float(value)

    >>> float_value
    1.23e-10

    >>> other_value = "0.0000001"
    >>> other_float_value = float(other_value)

    >>> other_float_value
    1e-07

Converting it back to a string would keep this notation:

    >>> str(float_value)
    '1.23e-10'

    >>> str(other_float_value)
    '1e-07'

The function `float_to_string` converts the float value without exponential notation:

    >>> api.float_to_string(float_value)
    '0.000000000123'

    >>> api.float_to_string(float_value) == value
    True

Passing in the string value should convert it to the same value:

    >>> api.float_to_string(value) == value
    True

When the fraction contains more digits, it will retain them all and takes care of the trailing zero:

    >>> new_value = 0.000000000123777
    >>> api.float_to_string(new_value)
    '0.000000000123777'

Converting integers work as well:

    >>> int_value = 123
    >>> api.float_to_string(int_value)
    '123'

The function also ensures that floatable string values remain unchanged:

    >>> str_value = "1.99887766554433221100"
    >>> api.float_to_string(str_value) == str_value
    True

When a scientific notation is passed in, the function will return the decimals:

    >>> api.float_to_string(1e-1)
    '0.1'

    >>> api.float_to_string(1e0)
    '1'

    >>> api.float_to_string(1e1)
    '10'

    >>> api.float_to_string(1e-16)
    '0.0000000000000001'

    >>> api.float_to_string(1e+16)
    '10000000000000000'

    >>> api.float_to_string(1e16)
    '10000000000000000'

    >>> api.float_to_string(-1e-1)
    '-0.1'

    >>> api.float_to_string(-1e+1)
    '-10'


Convert to minutes
..................

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
.....................

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
.....................

Fetch a value of a registry record::

    >>> key = "Products.CMFPlone.i18nl10n.override_dateformat.Enabled"
    >>> api.get_registry_record(key)
    False

If the record is not found, the default is returned::

    >>> key = "non.existing.key"
    >>> api.get_registry_record(key, default="NX_KEY")
    'NX_KEY'


Create a display list
.....................

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
.........................

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


Converting a string to UTF8
...........................

This function encodes unicode strings to UTF8.

In this test we use the German letter `ä` which is in unicode `u'\xe4'`:

    >>> api.to_utf8("ä")
    '\xc3\xa4'

    >>> api.to_utf8("\xc3\xa4")
    '\xc3\xa4'

    >>> api.to_utf8(api.safe_unicode("ä"))
    '\xc3\xa4'

    >>> api.to_utf8(u"\xe4")
    '\xc3\xa4'

Unsupported types return either the default value or fail:

    >>> api.to_utf8(object())
    Traceback (most recent call last):
    ...
    APIError: Expected string type, got '<type 'object'>'

    >>> api.to_utf8(object(), default="")
    ''

Check if an object is a string
..............................

This function checks if the given object is a string type.

    >>> api.is_string("Hello World")
    True

    >>> api.is_string(u"Hello World")
    True

    >>> api.is_string(r"Hello World")
    True

    >>> api.is_string("")
    True

    >>> api.is_string(None)
    False

    >>> api.is_string(object)
    False

Check if an object is a list
..............................

This function checks if the given object is a list type.

    >>> api.is_list([])
    True

    >>> api.is_list([1,2,3])
    True

    >>> api.is_list(set())
    False

    >>> api.is_list(tuple())
    False

    >>> api.is_list("[]")
    False


Check if an object is list iterable
...................................

This function checks if the given object can be handled like a list:

    >>> api.is_list_iterable([])
    True

    >>> api.is_list_iterable([1,2,3])
    True

    >>> api.is_list_iterable(set())
    True

    >>> api.is_list_iterable(tuple())
    True

    >>> api.is_list_iterable(dict())
    False

    >>> api.is_list_iterable("[]")
    False


Check if an object is temporary
...............................

This function checks if the given object is temporary. This is the object is
being created and is not yet ready.

Check the client we created earlier is not temporary:

    >>> api.is_temporary(client)
    False

Check with a step-by-step DX content type:

    >>> import uuid
    >>> from bika.lims.utils import tmpID
    >>> from zope.component import getUtility
    >>> from zope.component.interfaces import IFactory
    >>> from zope.event import notify
    >>> from zope.lifecycleevent import ObjectCreatedEvent

    >>> portal_types = api.get_tool("portal_types")
    >>> fti = portal_types.getTypeInfo("SampleContainer")
    >>> factory = getUtility(IFactory, fti.factory)
    >>> tmp_obj_id = tmpID()
    >>> tmp_obj = factory(tmp_obj_id)
    >>> tmp_obj._setPortalTypeName(fti.getId())
    >>> api.is_temporary(tmp_obj)
    True

    >>> tmp_obj.title = u'Test container'
    >>> notify(ObjectCreatedEvent(tmp_obj))
    >>> api.is_temporary(tmp_obj)
    True

The DX object is no longer temporary when is assigned to the parent folder and
the the definitive id is set:

    >>> folder = api.get_setup().sample_containers
    >>> uid = folder._setObject(tmp_obj_id, tmp_obj)
    >>> api.is_temporary(tmp_obj)
    True

    >>> tmp_obj_id = "non-uid-temp-id"
    >>> tmp_obj = folder._getOb(tmp_obj.getId())
    >>> tmp_obj.id = tmp_obj_id
    >>> api.is_temporary(tmp_obj)
    False

But even if we don't use a non-UID id as the temporary id on creation. System
will still consider the object as temporary until is assigned to its parent
folder:

    >>> tmp_obj = factory(tmp_obj_id)
    >>> tmp_obj._setPortalTypeName(fti.getId())
    >>> api.is_temporary(tmp_obj)
    True

    >>> tmp_obj.title = u'Test container 2'
    >>> notify(ObjectCreatedEvent(tmp_obj))
    >>> api.is_temporary(tmp_obj)
    True

    >>> folder = api.get_setup().sample_containers
    >>> uid = folder._setObject(tmp_obj_id, tmp_obj)
    >>> api.is_temporary(tmp_obj)
    True

    >>> tmp_obj = folder._getOb(tmp_obj.getId())
    >>> api.is_temporary(tmp_obj)
    False

On the other hand, an object with a UID id is always considered as temporary:

    >>> tmp_obj.id = uuid.uuid4().hex
    >>> api.is_temporary(tmp_obj)
    True

If we use `api.create`, the object returned is not temporary:

    >>> obj = api.create(setup.sample_containers, "SampleContainer", title="Another sample container")
    >>> api.is_temporary(obj)
    False

AT content types are considered temporary while being created inside
portal_factory:

    >>> tmp_path = "portal_factory/Client/{}".format(tmpID())
    >>> tmp_client = portal.clients.restrictedTraverse(tmp_path)
    >>> api.is_temporary(tmp_client)
    True

Copying content
...............

This function helps to do it right and copies an existing content for you.

Here we create a copy of the `Client` we created earlier::

    >>> client.setTaxNumber('VAT12345')
    >>> client2 = api.copy_object(client, title="Test Client 2")
    >>> client2
    <Client at /plone/clients/client-2>

    >>> client2.Title()
    'Test Client 2'

    >>> client2.getTaxNumber()
    'VAT12345'

We can override source values on copy as well::

    >>> client.setBankName('Peanuts Bank Ltd')
    >>> client3 = api.copy_object(client, title="Test Client 3",
    ...                           BankName="Nuts Bank Ltd")
    >>> client3
    <Client at /plone/clients/client-3>

    >>> client3.Title()
    'Test Client 3'

    >>> client3.getTaxNumber()
    'VAT12345'

    >>> client3.getBankName()
    'Nuts Bank Ltd'

We can create a copy in a container other than source's::

    >>> sample_points = self.portal.setup.samplepoints
    >>> sample_point = api.create(sample_points, "SamplePoint", title="Test")
    >>> sample_point
    <SamplePoint at /plone/setup/samplepoints/samplepoint-1>

    >>> sample_point_copy = api.copy_object(sample_point, container=client3)
    >>> sample_point_copy
    <SamplePoint at /plone/clients/client-3/samplepoint-2>

We can even create a copy to a different type::

    >>> suppliers = self.portal.bika_setup.bika_suppliers
    >>> supplier = api.copy_object(client, container=suppliers,
    ...                            portal_type="Supplier", title="Supplier 1")
    >>> supplier
    <Supplier at /plone/bika_setup/bika_suppliers/supplier-1>

    >>> supplier.Title()
    'Supplier 1'

    >>> supplier.getTaxNumber()
    'VAT12345'

    >>> supplier.getBankName()
    'Peanuts Bank Ltd'

It works for Dexterity types as well::

    >>> sample_containers = self.portal.bika_setup.sample_containers
    >>> sample_container = api.create(sample_containers, "SampleContainer",
    ...                               title="Source Sample Container",
    ...                               description="Sample container to test",
    ...                               capacity="100 ml")

    >>> sample_container.Title()
    'Source Sample Container'

    >>> sample_container.Description()
    'Sample container to test'

    >>> sample_container.getCapacity()
    '100 ml'

    >>> sample_container_copy = api.copy_object(sample_container,
    ...                                         title="Target Sample Container",
    ...                                         capacity="50 ml")

    >>> sample_container_copy.Title()
    'Target Sample Container'

    >>> sample_container_copy.Description()
    'Sample container to test'

    >>> sample_container_copy.getCapacity()
    '50 ml'


Parse to JSON
.............

    >>> api.parse_json('["a", "b", "c"]')
    [u'a', u'b', u'c']

    >>> obj = api.parse_json('{"a": 1, "b": 2, "c": 3}')
    >>> [obj[key] for key in 'abc']
    [1, 2, 3]

    >>> obj = api.parse_json('{"a": 1, "b": ["one", "two", 3], "c": 3}')
    >>> [obj[key] for key in 'abc']
    [1, [u'one', u'two', 3], 3]

    >>> api.parse_json("ko")
    ''

    >>> api.parse_json("ko", default="ok")
    'ok'

Convert to list
...............

    >>> api.to_list(None)
    [None]

    >>> api.to_list(["a", "b", "c"])
    ['a', 'b', 'c']

    >>> api.to_list('["a", "b", "c"]')
    [u'a', u'b', u'c']

    >>> api.to_list("a, b, c")
    ['a, b, c']

    >>> api.to_list([{"a": 1}, {"b": 2}, {"c": 3}])
    [{'a': 1}, {'b': 2}, {'c': 3}]

    >>> api.to_list('[{"a": 1}, {"b": 2}, {"c": 3}]')
    [{u'a': 1}, {u'b': 2}, {u'c': 3}]

    >>> api.to_list({"a": 1})
    [{'a': 1}]

    >>> api.to_list('{"a": 1, "b": ["one", "two", 3], "c": 3}')
    ['{"a": 1, "b": ["one", "two", 3], "c": 3}']

    >>> api.to_list(["[1, 2, 3]", "b", "c"])
    ['[1, 2, 3]', 'b', 'c']

    >>> api.to_list('["[1, 2, 3]", "b", "c"]')
    [u'[1, 2, 3]', u'b', u'c']


Un-catalog an object
....................

This function un-catalogs an object from **all** catalogs:

    >>> api.uncatalog_object(client)
    >>> uid = api.get_uid(client)
    >>> catalogs = api.get_catalogs_for(client)
    >>> matches = [cat(UID=uid) for cat in catalogs]
    >>> any(matches)
    False

Even from `uid_catalog`:

    >>> uc = api.get_tool("uid_catalog")
    >>> any(uc(UID=uid))
    False

Catalog an object
.................

This function (re)catalogs an object in **all** catalogs:

    >>> api.catalog_object(client)
    >>> uid = api.get_uid(client)
    >>> catalogs = api.get_catalogs_for(client)
    >>> matches = [cat(UID=uid) for cat in catalogs]
    >>> all(matches)
    True

Even in `uid_catalog`:

    >>> uc = api.get_tool("uid_catalog")
    >>> len(uc(UID=uid)) == 1
    True


Delete an object
................

This function deletes an object from the system.
Create a copy of an object created earlier:

    >>> new_client = api.copy_object(client, title="Client to delete")
    >>> uid = api.get_uid(new_client)
    >>> path = api.get_path(new_client)

Trying to delete an object without enough permissions is not possible:

    >>> api.delete(new_client)
    Traceback (most recent call last):
    ...
    Unauthorized: Do not have permissions to remove this object

Unless we explicitly tell the system to bypass security check:

    >>> api.delete(new_client, check_permissions=False)
    >>> api.get_object_by_uid(uid)
    Traceback (most recent call last):
    ...
    APIError: No object found for UID ...

    >>> obj = api.get_object_by_path(path)
    >>> api.is_object(obj)
    False


Move an object
..............

This function moves an object from its container to another.

Create the source and destination clients:

    >>> orig = api.create(portal.clients, "Client", title="Source Client")
    >>> dest = api.create(portal.clients, "Client", title="Destination Client")

Create a new contact in the source client:

    >>> contact = api.create(orig, "Contact", Firstname="John", Lastname="Wrong")

Move the contact to the destination client:

    >>> id = api.get_id(contact)
    >>> orig.hasObject(id)
    True
    >>> dest.hasObject(id)
    False
    >>> contact
    <Contact at /plone/clients/client-5/contact-2>
    >>> contact = api.move_object(contact, dest, check_constraints=False)
    >>> api.get_parent(contact) == dest
    True
    >>> dest.hasObject(id)
    True
    >>> orig.hasObject(id)
    False
    >>> contact
    <Contact at /plone/clients/client-6/contact-2>

It does nothing if destination is the same as the origin:

    >>> contact = api.move_object(contact, dest)
    >>> dest.hasObject(id)
    True

Trying to move the object into itself is not possible:

    >>> api.move_object(contact, contact)
    Traceback (most recent call last):
    [...]
    ValueError: Cannot move object into itself: <Contact at contact-2>

Trying to move an object to another folder without permissions is not possible:

    >>> contact = api.move_object(contact, orig)
    Traceback (most recent call last):
    [...]
    Unauthorized: Do not have permissions to remove this object

Unless we grant enough permissions to remove the object from origin:

    >>> from bika.lims.api.security import grant_permission_for
    >>> grant_permission_for(contact, "Delete objects", ["Authenticated"])
    >>> contact = api.move_object(contact, orig)
    >>> orig.hasObject(id)
    True
    >>> dest.hasObject(id)
    False
    >>> contact
    <Contact at /plone/clients/client-5/contact-2>

Still, destination container must allow the object's type:

    >>> contact = api.move_object(contact, setup)
    Traceback (most recent call last):
    [...]
    ValueError: Disallowed subobject type: Contact
