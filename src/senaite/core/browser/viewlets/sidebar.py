# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from bika.lims import api
from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from zope.component import getMultiAdapter


class SidebarViewletManager(OrderedViewletManager):
    """Viewlet manager for the sidebar

    The sidebar navigation is loaded dynamically via JavaScript from the
    @@sidebar-navigation-json API endpoint. This viewlet manager only
    handles the sidebar template rendering and availability checks.
    """
    custom_template = ViewPageTemplateFile("templates/sidebar.pt")

    def base_render(self):
        return super(SidebarViewletManager, self).render()

    def render(self):
        return self.custom_template()

    def available(self):
        """Check if sidebar should be shown"""
        is_anonymous = self.portal_state.anonymous()
        return not is_anonymous

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_portal_state"
        )

    def is_navbar_toggled(self):
        """Check if sidebar is toggled (permanently open)"""
        return self.request.cookies.get("sidebar-toggle", None) == "true"


class SidebarNavigationAPI(BrowserView):
    """JSON API endpoint for sidebar navigation

    Provides the navigation structure as JSON for dynamic sidebar loading.
    Access via: @@sidebar-navigation-json
    """

    def __init__(self, context, request):
        super(SidebarNavigationAPI, self).__init__(context, request)
        self._portal_types = None
        self._portal_state = None
        self._setup = None

    @property
    def portal_types(self):
        """Cached portal_types tool"""
        if self._portal_types is None:
            self._portal_types = api.get_tool("portal_types")
        return self._portal_types

    @property
    def portal_state(self):
        """Cached portal_state tool"""
        if self._portal_state is None:
            self._portal_state = api.get_view("plone_portal_state")
        return self._portal_state

    @property
    def setup(self):
        """Cached senaite setup"""
        if self._setup is None:
            self._setup = api.get_senaite_setup()
        return self._setup

    def get_navigation_root(self):
        """Return the navigation root
        """
        return self.portal_state.navigation_root()

    def get_navigation_depth(self, default=3):
        """Return the navigation depth from the setup
        """
        return getattr(self.setup, "sidebar_navigation_depth", default)

    def get_displayed_types(self, default=None):
        """Return the displayed types
        """
        return getattr(self.setup, "sidebar_displayed_types", default)

    def get_selected_folders(self, default=None):
        """Return the selected folders
        """
        if default is None:
            default = []
        return getattr(self.setup, "sidebar_folders", default)

    def __call__(self):
        """Return navigation tree as JSON"""
        self.request.response.setHeader("Content-Type", "application/json")

        try:
            # Get current URL from request parameter
            # JavaScript will send the current page URL
            current_url = self.request.get("current_url", "")

            # Get navigation tree
            tree = self.get_navigation_tree(current_url)

            result = {
                "success": True,
                "data": tree,
                "count": len(tree)
            }

        except Exception as e:
            # Log the error
            logger.error(
                "Error getting sidebar navigation: %s" % str(e),
                exc_info=True)

            result = {
                "success": False,
                "error": str(e),
                "data": []
            }

        return json.dumps(result)

    def get_navigation_tree(self, current_url=""):
        """Get the navigation tree as a structured dict

        Returns a hierarchical structure of navigation items that can be
        easily converted to JSON for the sidebar JavaScript.

        Uses uid_catalog to get all objects (including those in specialized
        catalogs like senaite_catalog_client, senaite_catalog_sample).

        :param current_url: The URL of the current page for highlighting
        """

        navigation_root = self.get_navigation_root()
        navigation_depth = self.get_navigation_depth()
        displayed_types = self.get_displayed_types()
        selected_folders = self.get_selected_folders()

        # Build tree using uid_catalog
        data = self._build_tree_from_uid_catalog(
            navigation_root,
            navigation_depth,
            displayed_types,
            selected_folders
        )

        # Process into JSON-friendly format
        return self._process_navigation_tree(data, current_url)

    def _build_tree_from_uid_catalog(
            self, navigation_root, navigation_depth, displayed_types,
            selected_folders=None):
        """Build navigation tree from uid_catalog

        Uses uid_catalog which indexes ALL content types, including those
        in specialized catalogs (senaite_catalog_client, etc.).

        :param navigation_root: The navigation root object
        :param navigation_depth: Maximum depth to query
        :param displayed_types: Tuple of portal types to include
        :param selected_folders: Tuple of folder IDs to include at root level
        :returns: Dict with tree structure
        """
        if selected_folders is None:
            selected_folders = ()
        uid_catalog = api.get_tool("uid_catalog")
        root_path_str = api.get_path(navigation_root)

        # Query uid_catalog for all navigation items
        # Note: uid_catalog doesn't have depth parameter, so we query all
        # and filter by depth later
        # Note: We DON'T filter by portal_type in the query because we want
        # selected_folders to always appear regardless of their type
        query = {
            "path": {"query": root_path_str},
            "sort_on": "id"
        }

        brains = uid_catalog(**query)

        # Build a mapping of path -> brain for quick lookup
        items_by_path = {}
        skipped_depth = 0
        skipped_root = 0
        skipped_type = 0

        for brain in brains:
            path = brain.getPath()

            # Normalize path - ensure it's absolute
            if not path.startswith("/"):
                # Relative path, prepend root path
                path = root_path_str + "/" + path

            # Calculate depth relative to navigation root
            depth = path.count("/") - root_path_str.count("/")

            # Skip items beyond max depth
            if depth > navigation_depth:
                skipped_depth += 1
                continue

            # Skip the root itself
            if path == root_path_str:
                skipped_root += 1
                continue

            obj = api.get_object(brain)
            obj_id = api.get_id(obj)
            portal_type = api.get_portal_type(obj)

            # Apply portal_type filtering
            # BUT: Skip filtering for selected_folders at root level (depth 1)
            # This ensures selected folders always appear in sidebar
            if displayed_types:
                is_selected_folder = (
                    depth == 1 and
                    selected_folders and
                    obj_id in selected_folders
                )
                if not is_selected_folder:
                    if portal_type not in displayed_types:
                        skipped_type += 1
                        continue

            items_by_path[path] = {
                "id": api.get_id(obj),
                "Title": api.get_title(obj),
                "Description": api.get_description(obj),
                "getURL": api.get_url(obj),
                "portal_type": api.get_portal_type(obj),
                "path": api.get_path(brain),
                "depth": depth,
                "review_state": api.get_review_status(brain),
                "show_children": True,
                "item": brain,
                "obj": obj,
                "children": []
            }

        # Build hierarchical structure
        root_children = []
        for path, item in items_by_path.items():
            # Find parent path
            parent_path = "/".join(path.split("/")[:-1])

            if parent_path == root_path_str:
                # Direct child of root
                root_children.append(item)
            elif parent_path in items_by_path:
                # Child of another item
                items_by_path[parent_path]["children"].append(item)

        # Filter root children if selected_folders is specified
        # and preserve the order from selected_folders
        if selected_folders:
            # Create a mapping of id -> item for quick lookup
            items_by_id = {
                item.get("id"): item for item in root_children
            }
            # Rebuild root_children in the order specified by selected_folders
            root_children = [
                items_by_id[folder_id]
                for folder_id in selected_folders
                if folder_id in items_by_id
            ]

        # Create sort key function using custom order
        def get_sort_key(item):
            """Get sort key for item based on custom order

            Items in selected_folders come first in specified order,
            others come after sorted alphabetically by id.
            """
            item_id = item.get("id", "")
            if item_id in selected_folders:
                # Return order index for items in custom order
                return (0, selected_folders.index(item_id))
            else:
                # Return high number + alphabetical for unlisted items
                return (1, item_id)

        # Sort children recursively
        def sort_children(node):
            if node.get("children"):
                node["children"].sort(key=get_sort_key)
                for child in node["children"]:
                    sort_children(child)

        for item in root_children:
            sort_children(item)

        # Sort root children using custom order
        root_children.sort(key=get_sort_key)

        return {"children": root_children}

    def _process_navigation_tree(self, tree_data, current_url=""):
        """Process navigation tree into a JSON-friendly structure

        :param tree_data: Dict with navigation tree data from portlet
        :param current_url: URL of the current page for highlighting
        :returns: List of navigation items with children
        """
        if not tree_data:
            return []

        # Normalize current URL for comparison (remove trailing slash)
        current_url = current_url.rstrip("/")

        items = []
        children = tree_data.get("children", [])

        for child in children:
            item = self._process_navigation_item(child, current_url)
            if item:
                items.append(item)

        return items

    def _process_navigation_item(self, node, current_url=""):
        """Process a single navigation item

        :param node: Navigation node dict
        :param current_url: URL of the current page for highlighting
        :returns: Processed navigation item dict
        """
        if not node:
            return None

        # Get item URL and normalize for comparison
        item_url = node.get("getURL", "").rstrip("/")

        # Normalize current URL - remove query params, anchors, and view names
        normalized_current = current_url.split("#")[0].split("?")[0].rstrip("/")

        # Remove common view suffixes from both URLs
        view_suffixes = [
            "/view", "/@@view", "/folder_contents", "/@@folder_contents",
            "/edit", "/@@edit", "/folder_listing", "/@@folder_listing"
        ]

        for view_suffix in view_suffixes:
            if normalized_current.endswith(view_suffix):
                normalized_current = normalized_current[:-len(view_suffix)]
                break

        # Also normalize item URL in case it has view suffixes
        normalized_item = item_url
        for view_suffix in view_suffixes:
            if normalized_item.endswith(view_suffix):
                normalized_item = normalized_item[:-len(view_suffix)]
                break

        # Check if this item is current or parent
        is_current = (normalized_item == normalized_current)
        is_parent = (
            normalized_current.startswith(normalized_item + "/")
            if normalized_item else False
        )

        # Get icon using the same approach as SENAITE's bootstrapview
        portal_type = node.get("portal_type", "")
        icon = ""

        if portal_type:
            try:
                # Get FTI (Factory Type Information) for the portal type
                fti = self.portal_types.getTypeInfo(portal_type)
                if fti:
                    # Use getIcon() method - returns path like
                    # "senaite_theme/icon/client"
                    icon = fti.getIcon() or ""
            except Exception as e:
                logger.warning(
                    "Could not get icon for type %s: %s" % (
                        str(portal_type), str(e)))

        item = {
            "id": node.get("id", ""),
            "title": node.get("Title", ""),
            "description": node.get("Description", ""),
            "url": item_url,
            "icon": icon,
            "review_state": node.get("review_state", ""),
            "is_current": is_current,
            "is_parent": is_parent,
            "is_folderish": node.get("show_children", False),
            "portal_type": node.get("portal_type", ""),
            "depth": node.get("depth", 0),
            "children": []
        }

        # Process children recursively
        children = node.get("children", [])
        for child in children:
            child_item = self._process_navigation_item(child, current_url)
            if child_item:
                item["children"].append(child_item)
                # If any child is current, mark this as parent
                if child_item["is_current"] or child_item["is_parent"]:
                    item["is_parent"] = True

        return item
