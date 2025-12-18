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
        return self.setup.getSidebarNavigationDepth()

    def get_displayed_types(self, default=None):
        """Return the displayed types
        """
        return self.setup.getSidebarDisplayedTypes()

    def get_selected_folders(self, default=None):
        """Return the selected folders
        """
        return self.setup.getSidebarFolders()

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

    def _create_item_from_brain(self, brain, depth):
        """Create navigation item dict from catalog brain

        :param brain: Catalog brain
        :param depth: Depth level of the item
        :returns: Dict with item data
        """
        return {
            "id": api.get_id(brain),
            "Title": api.get_title(brain),
            "Description": api.get_description(brain),
            "getURL": api.get_url(brain),
            "portal_type": api.get_portal_type(brain),
            "path": api.get_path(brain),
            "depth": depth,
            "review_state": api.get_review_status(brain),
            "show_children": True,
            "item": brain,
            "children": []
        }

    def _build_tree_from_uid_catalog(
            self, navigation_root, navigation_depth, displayed_types,
            selected_folders=None):
        """Build navigation tree

        Top-level folders are queried from portal_catalog by ID.
        Children are queried recursively from uid_catalog.

        If no folders are selected, returns an empty tree.

        :param navigation_root: The navigation root object
        :param navigation_depth: Maximum depth to query
        :param displayed_types: Tuple of portal types to include
        :param selected_folders: Tuple of folder IDs to include at root level
        :returns: Dict with tree structure
        """
        if selected_folders is None:
            selected_folders = ()

        root_children = []

        # Only build tree if folders are selected
        if not selected_folders:
            return {"children": root_children}

        # Get selected folders directly from portal_catalog by ID
        portal_catalog = api.get_tool("portal_catalog")
        root_path_str = api.get_path(navigation_root)

        for folder_id in selected_folders:
            # Query for folder by ID at root level
            query = {
                "path": {"query": root_path_str, "depth": 1},
                "id": folder_id
            }
            brains = portal_catalog(**query)

            if not brains:
                continue

            brain = brains[0]

            # Build folder item from brain
            folder_item = self._create_item_from_brain(brain, depth=1)

            # Query children using uid_catalog if depth allows
            if navigation_depth > 1:
                children = self._get_children_recursive(
                    brain,
                    max_depth=navigation_depth,
                    current_depth=1,
                    displayed_types=displayed_types
                )
                folder_item["children"] = children

            root_children.append(folder_item)

        return {"children": root_children}

    def _get_children_recursive(self, parent_brain, max_depth, current_depth,
                                displayed_types=None):
        """Recursively get children from uid_catalog

        :param parent_brain: Parent catalog brain
        :param max_depth: Maximum depth to query
        :param current_depth: Current depth level
        :param displayed_types: Tuple of portal types to include
        :returns: List of child items
        """
        if current_depth >= max_depth:
            return []

        uid_catalog = api.get_tool("uid_catalog")
        parent_path = api.get_path(parent_brain)

        # Query for all descendants
        # NOTE: The UID catalog uses relative paths w/o slash!
        query = {
            "path": {
                "query": parent_path.replace("/", "", 1),
            },
            "sort_on": "id"
        }
        if displayed_types:
            query["portal_type"] = displayed_types

        brains = uid_catalog(**query)

        # Build a mapping of path -> item
        items_by_path = {}

        for brain in brains:
            path = api.get_path(brain)

            # Skip parent itself
            if path == parent_path:
                continue

            # Calculate depth relative to parent
            depth = path.count("/") - parent_path.count("/")

            # Skip items beyond remaining depth
            if depth > (max_depth - current_depth):
                continue

            # Create item from brain
            item = self._create_item_from_brain(
                brain, depth=current_depth + depth)
            items_by_path[path] = item

        # Build hierarchical structure
        children = []
        for path, item in items_by_path.items():
            # Find parent path
            item_parent_path = "/".join(path.split("/")[:-1])

            if item_parent_path == parent_path:
                # Direct child of parent
                children.append(item)
            elif item_parent_path in items_by_path:
                # Child of another item
                items_by_path[item_parent_path]["children"].append(item)

        return children

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
