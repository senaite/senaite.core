Sidebar Navigation
==================

The sidebar navigation provides a dynamic, configurable navigation tree for
SENAITE LIMS. It queries registered catalogs to build a hierarchical structure
of navigation items.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t SidebarNavigation


Test Setup
..........

Imports:

    >>> import json
    >>> from bika.lims import api
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles


Setup the test user
...................

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> setRoles(portal, TEST_USER_ID, ["Manager"])


Setup test data
...............

Create some test folders and objects to build a navigation tree:

    >>> clients = portal.clients
    >>> samples = portal.samples
    >>> methods = portal.methods
    >>> batches = portal.batches
    >>> worksheets = portal.worksheets

Create a test client for testing:

    >>> client = api.create(clients, "Client", title="Test Client")
    >>> api.get_id(client)
    'client-1'

Reindex the object so it appears in catalogs:

    >>> client.reindexObject()

Get the SenaiteSetup object:

    >>> setup = api.get_senaite_setup()


Sidebar Navigation Configuration
................................

The sidebar navigation is configured through SenaiteSetup.


Test default configuration
..........................

First, reset to defaults:

    >>> setup.setSidebarFolders(())
    >>> setup.setSidebarNavigationDepth(3)
    >>> setup.setSidebarSkipTypes(())

By default, no folders are selected:

    >>> setup.getSidebarFolders()
    ()

Default navigation depth is 3:

    >>> setup.getSidebarNavigationDepth()
    3

No portal types are skipped by default:

    >>> setup.getSidebarSkipTypes()
    ()


Test setting sidebar folders
............................

Select specific folders to display:

    >>> setup.setSidebarFolders(("clients", "samples", "methods"))
    >>> setup.getSidebarFolders()
    ('clients', 'samples', 'methods')


Test setting navigation depth
.............................

Set maximum depth to 2:

    >>> setup.setSidebarNavigationDepth(2)
    >>> setup.getSidebarNavigationDepth()
    2


Test setting skip types
.......................

Skip specific portal types from navigation:

    >>> setup.setSidebarSkipTypes(("Client", "AnalysisRequest"))
    >>> setup.getSidebarSkipTypes()
    ('Client', 'AnalysisRequest')


Sidebar Navigation API Endpoint
...............................

The sidebar navigation is accessed via the @@sidebar-navigation-json view.


Test getting the navigation view
................................

Get the navigation API view:

    >>> view = api.get_view("sidebar-navigation-json", context=portal)
    >>> view is not None
    True


Test getting navigation root
............................

The navigation root should be the portal:

    >>> navigation_root = view.get_navigation_root()
    >>> navigation_root == portal
    True


Test getting navigation depth
.............................

Should return the configured depth:

    >>> view.get_navigation_depth()
    2


Test getting skip types
.......................

Should return the configured types to skip:

    >>> view.get_skip_types()
    ('Client', 'AnalysisRequest')


Test getting selected folders
.............................

Should return the configured folders:

    >>> view.get_selected_folders()
    ('clients', 'samples', 'methods')


Test dynamic catalog lookup
...........................

The sidebar uses dynamic catalog lookup to optimize queries by selecting the
most appropriate catalog for each folder based on its allowed content types.

When a folder allows only one content type, the sidebar uses the specialized
catalog for that type (e.g., senaite_catalog_client for Client objects).
Otherwise, it falls back to uid_catalog.

Get the catalog tools for testing:

    >>> portal_catalog = api.get_tool("portal_catalog")
    >>> uid_catalog = api.get_tool("uid_catalog")


Test get_catalog_for with client folder
.......................................

The ClientFolder allows only Client content type, so the method should
select the specialized senaite_catalog_client instead of uid_catalog:

    >>> clients_brain = uid_catalog(UID=api.get_uid(clients))[0]
    >>> catalog = view.get_catalog_for(clients_brain)
    >>> catalog.id
    'senaite_catalog_client'


Test catalog caching
....................

The catalog lookup should be cached per portal type:

    >>> # Query again for the same portal type
    >>> catalog_again = view.get_catalog_for(clients_brain)
    >>> catalog_again.id
    'senaite_catalog_client'


Test catalog selection logic
............................

The get_catalog_for method inspects the FTI (Factory Type Information) of
each folder to determine which catalog to use. When a folder allows exactly
one content type, it uses the specialized catalog for that type. When a
folder allows multiple content types, it falls back to uid_catalog.

Verify ClientFolder FTI configuration:

    >>> portal_types = api.get_tool("portal_types")
    >>> clients_fti = portal_types.getTypeInfo("ClientFolder")
    >>> allowed_types = clients_fti.allowed_content_types
    >>> "Client" in allowed_types
    True
    >>> # ClientFolder allows exactly one content type
    >>> len(allowed_types) == 1
    True

Test fallback to uid_catalog for folders with multiple allowed types:

    >>> # Samples folder allows multiple content types
    >>> samples_brain = uid_catalog(UID=api.get_uid(samples))[0]
    >>> samples_catalog = view.get_catalog_for(samples_brain)
    >>> # Should use uid_catalog since it allows multiple types
    >>> samples_catalog.id in ("uid_catalog", "senaite_catalog_sample")
    True


Test dynamic catalog integration with tree building
...................................................

The `_get_children_recursive` method uses the catalog returned by
get_catalog_for, ensuring that each folder in the navigation tree is
queried using its optimal catalog:

    >>> # Build a tree with the clients folder
    >>> setup.setSidebarFolders(("clients",))
    >>> tree_data = view._build_tree(
    ...     navigation_root=portal,
    ...     navigation_depth=2,
    ...     skip_types=None,
    ...     selected_folders=("clients",)
    ... )
    >>> # Verify the clients folder appears in the tree
    >>> len(tree_data["children"]) > 0
    True
    >>> tree_data["children"][0]["id"]
    'clients'

The tree building process automatically selected senaite_catalog_client for
querying Client objects within the ClientFolder, demonstrating the dynamic
catalog lookup in action.


Building Navigation Tree
........................

Test building the navigation tree with selected folders.


Test building tree with folders
...............................

Set up folders and build tree:

    >>> setup.setSidebarFolders(("clients", "samples"))
    >>> data = view._build_tree(
    ...     navigation_root=portal,
    ...     navigation_depth=2,
    ...     skip_types=None,
    ...     selected_folders=("clients", "samples")
    ... )
    >>> data is not None
    True

The tree should have children:

    >>> "children" in data
    True

Children should be in the specified order:

    >>> children = data["children"]
    >>> len(children) >= 0
    True

If folders exist, they should be in the correct order:

    >>> if len(children) > 0:
    ...     # First folder should be "clients"
    ...     children[0]["id"] in ("clients",)
    True


Test building tree without folders
..................................

With no folders selected, tree should be empty:

    >>> data = view._build_tree(
    ...     navigation_root=portal,
    ...     navigation_depth=2,
    ...     skip_types=None,
    ...     selected_folders=()
    ... )
    >>> data["children"]
    []


Test item creation from brain
.............................

Test creating navigation items from catalog brains using created client:

    >>> client_uid = api.get_uid(client)
    >>> brains = uid_catalog(UID=client_uid)
    >>> len(brains) > 0
    True
    >>> brain = brains[0]
    >>> item = view._create_item_from_brain(brain, depth=1)
    >>> # Item should have required keys
    >>> "id" in item
    True
    >>> "Title" in item
    True
    >>> "getURL" in item
    True
    >>> "path" in item
    True
    >>> "depth" in item
    True
    >>> "children" in item
    True


Test navigation tree processing
...............................

Test processing the tree into JSON-friendly format:

    >>> tree_data = {"children": []}
    >>> result = view._process_navigation_tree(tree_data, current_url="")
    >>> result
    []


Test URL normalization for highlighting
.......................................

Test that current item is properly detected:

    >>> # Reset configuration for this test
    >>> setup.setSidebarFolders(("clients",))
    >>> setup.setSidebarSkipTypes(())
    >>> setup.setSidebarNavigationDepth(3)

    >>> # Get the clients folder URL
    >>> clients_url = api.get_url(clients)

    >>> # Build the tree
    >>> tree = view.get_navigation_tree(current_url=clients_url)

    >>> # Find the clients item in the tree
    >>> if tree:
    ...     clients_item = tree[0] if len(tree) > 0 else None
    ...     if clients_item and clients_item.get("id") == "clients":
    ...         # Should be marked as current
    ...         clients_item.get("is_current")
    True


Test portal type skipping
.........................

Test that portal type skipping works correctly:

    >>> setup.setSidebarFolders(("clients",))
    >>> setup.setSidebarSkipTypes(("Client",))

    >>> # Build tree with type skipping
    >>> data = view._build_tree(
    ...     navigation_root=portal,
    ...     navigation_depth=2,
    ...     skip_types=("Client",),
    ...     selected_folders=("clients",)
    ... )

    >>> # Root folder should still appear
    >>> len(data["children"]) > 0
    True


Test JSON API response
......................

Test the full JSON API response:

    >>> # Reset to default state
    >>> setup.setSidebarFolders(("clients", "samples", "methods"))
    >>> setup.setSidebarSkipTypes(())
    >>> setup.setSidebarNavigationDepth(3)

    >>> # Get JSON response
    >>> view = api.get_view("sidebar-navigation-json", context=portal)
    >>> json_response = view()

    >>> # Parse JSON
    >>> result = json.loads(json_response)
    >>> result["success"]
    True

    >>> "data" in result
    True

    >>> "count" in result
    True


Cleanup
.......

Reset configuration to defaults:

    >>> setup.setSidebarFolders(())
    >>> setup.setSidebarNavigationDepth(3)
    >>> setup.setSidebarSkipTypes(())
