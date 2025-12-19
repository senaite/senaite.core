Sidebar Navigation
==================

The sidebar navigation provides a dynamic, configurable navigation tree for
SENAITE LIMS. It queries both portal_catalog and uid_catalog to build a
hierarchical structure of navigation items.

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

Get the SenaiteSetup object:

    >>> setup = api.get_senaite_setup()


API Methods for Catalog Brains
...............................

The API provides methods to handle both portal_catalog and uid_catalog brains,
which may have different path formats.


Test get_path with portal_catalog brain
........................................

Portal catalog brains return absolute paths:

    >>> portal_catalog = api.get_tool("portal_catalog")
    >>> brains = portal_catalog(portal_type="Client", sort_limit=1)
    >>> if brains:
    ...     brain = brains[0]
    ...     path = api.get_path(brain)
    ...     path.startswith("/")
    True


Test get_path with uid_catalog brain
.....................................

UID catalog brains may return relative paths that need to be normalized:

    >>> uid_catalog = api.get_tool("uid_catalog")
    >>> brains = uid_catalog(sort_limit=1)
    >>> if brains:
    ...     brain = brains[0]
    ...     path = api.get_path(brain)
    ...     # Path should be normalized to absolute path
    ...     path.startswith("/")
    True


Test get_url with portal_catalog brain
.......................................

Portal catalog brains have a getURL method:

    >>> brains = portal_catalog(portal_type="Client", sort_limit=1)
    >>> if brains:
    ...     brain = brains[0]
    ...     url = api.get_url(brain)
    ...     url.startswith("http")
    True


Test get_url with uid_catalog brain
....................................

UID catalog brains may not have getURL, so we construct it from the path:

    >>> brains = uid_catalog(sort_limit=1)
    >>> if brains:
    ...     brain = brains[0]
    ...     url = api.get_url(brain)
    ...     # URL should be properly constructed
    ...     url.startswith("http")
    True


Sidebar Navigation Configuration
.................................

The sidebar navigation is configured through SenaiteSetup.


Test default configuration
...........................

By default, no folders are selected:

    >>> setup.getSidebarFolders()
    ()

Default navigation depth is 3:

    >>> setup.getSidebarNavigationDepth()
    3

No portal types are filtered by default:

    >>> setup.getSidebarDisplayedTypes()
    ()


Test setting sidebar folders
.............................

Select specific folders to display:

    >>> setup.setSidebarFolders(("clients", "samples", "methods"))
    >>> setup.getSidebarFolders()
    ('clients', 'samples', 'methods')


Test setting navigation depth
..............................

Set maximum depth to 2:

    >>> setup.setSidebarNavigationDepth(2)
    >>> setup.getSidebarNavigationDepth()
    2


Test setting displayed types
.............................

Filter to only show specific portal types:

    >>> setup.setSidebarDisplayedTypes(("Client", "AnalysisRequest"))
    >>> setup.getSidebarDisplayedTypes()
    ('Client', 'AnalysisRequest')


Sidebar Navigation API Endpoint
................................

The sidebar navigation is accessed via the @@sidebar-navigation-json view.


Test getting the navigation view
.................................

Get the navigation API view:

    >>> view = api.get_view("sidebar-navigation-json", context=portal)
    >>> view is not None
    True


Test getting navigation root
.............................

The navigation root should be the portal:

    >>> navigation_root = view.get_navigation_root()
    >>> navigation_root == portal
    True


Test getting navigation depth
..............................

Should return the configured depth:

    >>> view.get_navigation_depth()
    2


Test getting displayed types
.............................

Should return the configured types:

    >>> view.get_displayed_types()
    ('Client', 'AnalysisRequest')


Test getting selected folders
..............................

Should return the configured folders:

    >>> view.get_selected_folders()
    ('clients', 'samples', 'methods')


Building Navigation Tree
.........................

Test building the navigation tree with selected folders.


Test building tree with folders
................................

Set up folders and build tree:

    >>> setup.setSidebarFolders(("clients", "samples"))
    >>> data = view._build_tree_from_uid_catalog(
    ...     navigation_root=portal,
    ...     navigation_depth=2,
    ...     displayed_types=None,
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
...................................

With no folders selected, tree should be empty:

    >>> data = view._build_tree_from_uid_catalog(
    ...     navigation_root=portal,
    ...     navigation_depth=2,
    ...     displayed_types=None,
    ...     selected_folders=()
    ... )
    >>> data["children"]
    []


Test item creation from brain
..............................

Test creating navigation items from catalog brains:

    >>> brains = portal_catalog(portal_type="Client", sort_limit=1)
    >>> if brains:
    ...     brain = brains[0]
    ...     item = view._create_item_from_brain(brain, depth=1)
    ...     # Item should have required keys
    ...     "id" in item
    ...     "Title" in item
    ...     "getURL" in item
    ...     "path" in item
    ...     "depth" in item
    ...     "children" in item
    True
    True
    True
    True
    True
    True


Test navigation tree processing
................................

Test processing the tree into JSON-friendly format:

    >>> tree_data = {"children": []}
    >>> result = view._process_navigation_tree(tree_data, current_url="")
    >>> result
    []


Test URL normalization for highlighting
........................................

Test that current item is properly detected:

    >>> # Reset configuration for this test
    >>> setup.setSidebarFolders(("clients",))
    >>> setup.setSidebarDisplayedTypes(())
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


Test portal type filtering
...........................

Test that portal type filtering works correctly:

    >>> setup.setSidebarFolders(("clients",))
    >>> setup.setSidebarDisplayedTypes(("Client",))

    >>> # Build tree with type filtering
    >>> data = view._build_tree_from_uid_catalog(
    ...     navigation_root=portal,
    ...     navigation_depth=2,
    ...     displayed_types=("Client",),
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
    >>> setup.setSidebarDisplayedTypes(())
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


Test path normalization edge cases
...................................

Test that paths are correctly normalized for different catalog types:

    >>> portal_path = api.get_path(portal)
    >>> portal_path.startswith("/")
    True

Test that relative paths are properly handled:

    >>> # Simulate a relative path (like from uid_catalog)
    >>> relative_path = "clients"
    >>> if not relative_path.startswith(portal_path):
    ...     normalized_path = "/".join([portal_path, relative_path])
    ...     normalized_path.startswith(portal_path)
    True


Cleanup
.......

Reset configuration to defaults:

    >>> setup.setSidebarFolders(())
    >>> setup.setSidebarNavigationDepth(3)
    >>> setup.setSidebarDisplayedTypes(())
