# Sidebar Navigation

The sidebar navigation provides a collapsible folder tree on the
left side of the SENAITE UI. It is implemented as a Plone viewlet
manager with a React frontend that loads navigation data
asynchronously from a JSON API endpoint.


## Components

`sidebar.py`
    Contains two classes:
    - `SidebarViewletManager`: Controls sidebar rendering and
      availability. The `available()` method gates the entire
      sidebar based on the `ViewNavigation` permission.
    - `SidebarNavigationAPI`: JSON endpoint at
      `@@sidebar-navigation-json` that builds the navigation tree
      from configured sidebar folders.

`templates/sidebar.pt`
    The sidebar container template rendered by the viewlet manager.


## Permissions

### senaite.core: View Navigation

Controls whether the sidebar is rendered at all. Checked on the
portal root in `SidebarViewletManager.available()`.

Granted to all SENAITE roles in `rolemap.xml` with `acquire=False`:
- Analyst, Client, LabClerk, LabManager, Manager
- Preserver, Publisher, RegulatoryInspector
- Sampler, SamplingCoordinator, Verifier

Users with only `Member` or `Authenticated` roles (no SENAITE role)
will not see the sidebar.

### Folder-level visibility

Individual folders within the sidebar are filtered by the catalog
query in `_build_tree()`. The `portal_catalog` query respects the
`allowedRolesAndUsers` index, so folders the user cannot `View`
are excluded from the navigation tree.

Folder visibility is determined by the workflow assigned to each
folder type:
- `senaite_one_state_workflow` (Samples, Methods, etc.):
  All permissions acquired from the portal root.
- `senaite_batches_workflow` (BatchFolder):
  All permissions acquired, Delete restricted to lab roles.
- `senaite_clients_workflow` (ClientFolder):
  View/Access/List set to `acquire=False` with explicit lab roles.
  Client role is excluded, so clients cannot see the clients
  listing in the sidebar.
- `senaite_worksheets_workflow` (Worksheets):
  Permissions vary by workflow state.


## Configuration

The sidebar content is configured in SENAITE Setup under the
Appearance fieldset:

`sidebar_folders`
    Tuple of folder IDs to show at the root level.
    Default: `("clients", "samples", "methods", "batches",
    "worksheets")`

`sidebar_navigation_depth`
    Maximum depth for recursive child queries (1-3).
    Default: `1`

`sidebar_skip_types`
    Portal types to exclude from the navigation tree.
    Default: `("AnalysisRequest", "Attachment")`


## Data Flow

1. Page loads, sidebar template renders the container
2. React component requests `@@sidebar-navigation-json`
3. `SidebarNavigationAPI` reads `getSidebarFolders()` from setup
4. Queries `portal_catalog` for each folder ID at root level
5. Recursively queries children via `uid_catalog` up to max depth
6. Returns JSON tree structure to the React component
7. React renders the collapsible navigation tree
