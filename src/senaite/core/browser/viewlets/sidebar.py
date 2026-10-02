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
import Missing

from bika.lims import api
from bika.lims.api.security import check_permission
from senaite.core.permissions import ViewNavigation
from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.memoize.instance import memoize
from Products.CMFCore.permissions import View
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from senaite.core.catalog import get_catalogs_by_type
from senaite.core.i18n import translate
from senaite.core.interfaces.catalog import ISenaiteCatalogObject
from zope.component import getMultiAdapter

UID_CATALOG = "uid_catalog"


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
        if self.portal_state.anonymous():
            return False
        portal = self.portal_state.portal()
        return check_permission(ViewNavigation, portal)

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
        self._catalog_cache = {}

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

    def get_skip_types(self, default=None):
        """Return the types to skip
        """
        return self.setup.getSidebarSkipTypes()

    def get_selected_folders(self, default=None):
        """Return the selected folders
        """
        return self.setup.getSidebarFolders()

    def get_catalog_for(self, brain_or_object):
        """Return the appropriate catalog for the given parent
        """
        portal_type = api.get_portal_type(brain_or_object)

        # Check cache first
        if portal_type in self._catalog_cache:
            return self._catalog_cache[portal_type]

        catalog = UID_CATALOG
        fti = self.portal_types.getTypeInfo(portal_type)
        allowed_contents = fti.allowed_content_types or []
        if len(allowed_contents) == 1:
            child_type = allowed_contents[0]
            catalogs = get_catalogs_by_type(api.to_utf8(child_type))
            if catalogs:
                catalog = catalogs[0]

        catalog_tool = api.get_tool(catalog)
        self._catalog_cache[portal_type] = catalog_tool
        return catalog_tool

    def __call__(self):
        """Return navigation tree as JSON"""
        self.request.response.setHeader("Content-Type", "application/json")

        try:
            # Get current URL from request parameter
            current_url = self.request.get("current_url", "")

            # Check if we should show more items (expanded limit)
            show_more = self.request.get("show_more", "false") == "true"

            # Get navigation tree
            tree = self.get_navigation_tree(current_url, show_more=show_more)

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

    def get_navigation_tree(self, current_url="", show_more=False):
        """Get the navigation tree as a structured dict

        Returns a hierarchical structure of navigation items that can be
        easily converted to JSON for the sidebar JavaScript.

        Uses uid_catalog to get all objects (including those in specialized
        catalogs like senaite_catalog_client, senaite_catalog_sample).

        :param current_url: The URL of the current page for highlighting
        :param show_more: If True, show more items with expanded limit
        """

        navigation_root = self.get_navigation_root()
        navigation_depth = self.get_navigation_depth()
        skip_types = self.get_skip_types()
        selected_folders = self.get_selected_folders()

        # Build tree using uid_catalog
        data = self._build_tree(
            navigation_root,
            navigation_depth,
            skip_types,
            selected_folders,
            show_more=show_more
        )

        # Process into JSON-friendly format
        return self._process_navigation_tree(data, current_url)

    def _build_tree(self, navigation_root, navigation_depth, skip_types,
                    selected_folders=None, show_more=False):
        """Build navigation tree

        Top-level folders are looked up by ID in the navigation root and
        filtered by the View permission. Children are queried recursively
        from the catalogs.

        If no folders are selected, returns an empty tree.

        :param navigation_root: The navigation root object
        :param navigation_depth: Maximum depth to query
        :param skip_types: Tuple of portal types to exclude
        :param selected_folders: Tuple of folder IDs to include at root level
        :param show_more: If True, show more items with expanded limit
        :returns: Dict with tree structure
        """
        if selected_folders is None:
            selected_folders = ()

        root_children = []

        # Only build tree if folders are selected
        if not selected_folders:
            return {"children": root_children}

        for folder_id in selected_folders:
            # Get the selected folder directly from the navigation root
            folder = navigation_root.get(folder_id)

            if folder is None:
                continue

            # Filter by permission instead of by `allowedRolesAndUsers`.
            #
            # The `Client` role is granted dynamically by the local role
            # providers in `senaite.core.security.clientrole`, and their
            # `getAllRoles` deliberately returns nothing so that linking a
            # contact does not force a catalog reindex. A role granted that
            # way never reaches the `allowedRolesAndUsers` index, so a
            # catalog query hides root folders the user can actually reach:
            # the folder is traversable and editable, but absent from the
            # navigation bar.
            #
            # The selected folders are an explicit, bounded setup value, so
            # waking them up to ask the same question traversal asks is
            # cheap and cannot disagree with what the user gets on click.
            if not check_permission(View, folder):
                continue

            # Build folder item from the object
            folder_item = self._create_item(folder, depth=1)

            # Skip invalid items
            if folder_item is None:
                continue

            # Query children using the catalogs if depth allows
            if navigation_depth > 1:
                children_data = self._get_children_recursive(
                    folder,
                    max_depth=navigation_depth,
                    current_depth=1,
                    skip_types=skip_types,
                    show_more=show_more
                )
                folder_item["children"] = children_data.get("items", [])
                folder_item["has_more"] = children_data.get("has_more", False)
                folder_item["total_count"] = children_data.get(
                    "total_count", 0)

            root_children.append(folder_item)

        return {"children": root_children}

    def _create_item(self, brain_or_object, depth):
        """Create navigation item dict from a catalog brain or an object

        Root folders are passed as objects (they are filtered by permission,
        not by catalog query), children as catalog brains.

        :param brain_or_object: Catalog brain or content object
        :param depth: Depth level of the item
        :returns: Dict with item data or None if the item is invalid
        """
        try:
            item = {
                "id": api.get_id(brain_or_object),
                "Title": api.get_title(brain_or_object),
                "Description": api.get_description(brain_or_object),
                "getURL": api.get_url(brain_or_object),
                "portal_type": api.get_portal_type(brain_or_object),
                "path": api.get_path(brain_or_object),
                "depth": depth,
                "review_state": api.get_review_status(brain_or_object),
                "show_children": True,
                "item": brain_or_object,
                "children": []
            }

            # Check each value for Missing.Value
            for key, value in item.items():
                if value is Missing.Value:
                    raise ValueError(
                        "%s is Missing.Value" % key)

            return item

        except Exception as e:
            # Log and skip invalid items (e.g. stale catalog entries)
            logger.warning("Could not create item from %r: %s"
                           % (brain_or_object, str(e)))
            return None

    def _get_children_recursive(self, parent, max_depth, current_depth,
                                skip_types=None, show_more=False):
        """Recursively get children using catalog depth=1 query

        Uses a catalog query with depth=1 for optimal performance on large
        databases. Does not wake up any of the children.

        Children stay catalog-filtered on purpose: they can be many, and
        their `allowedRolesAndUsers` does carry the tokens client users are
        queried with (`user:<id>` from local roles, `client:<uid>` from
        `senaite.core.catalog.indexer.allowedrolesandusers`).

        :param parent: Parent object or catalog brain
        :param max_depth: Maximum depth to query
        :param current_depth: Current depth level
        :param skip_types: Tuple of portal types to exclude
        :param show_more: If True, show more items with expanded limit
        :returns: Dict with items, has_more flag, and total_count
        """
        if current_depth >= max_depth:
            return {"items": [], "has_more": False, "total_count": 0}

        parent_path = api.get_path(parent)
        catalog = self.get_catalog_for(parent)

        # Query for immediate children only (depth=1)
        query = {
            "path": {
                "query": parent_path,
                "depth": 1,
            },
            "sort_on": "path",
            "sort_order": "descending",
        }

        # update query for active items if senaite catalog
        if ISenaiteCatalogObject.providedBy(catalog):
            query.update({
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending",
            })

        logger.info("Query catalog %s for children of %s at depth %d: %s" % (
            catalog.id, parent_path, current_depth, str(query)))

        brains = catalog(**query)

        # Build items for children, filtering skip_types in the loop
        children = []
        has_more = False
        limit = 10
        skip_types = skip_types or ()

        for brain in brains:
            # Skip types that should be excluded
            portal_type = api.get_portal_type(brain)
            if portal_type in skip_types:
                continue

            # Check limit only when not showing more items
            if not show_more and len(children) >= limit:
                has_more = True
                break

            # Create item from brain
            item = self._create_item(
                brain, depth=current_depth + 1)

            # Skip invalid items (stale catalog entries)
            if item is None:
                continue

            # Recursively get children if we haven't reached max depth
            if current_depth + 1 < max_depth:
                children_data = self._get_children_recursive(
                    brain,
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                    skip_types=skip_types,
                    show_more=show_more
                )
                item["children"] = children_data.get("items", [])
                item["has_more"] = children_data.get("has_more", False)
                item["total_count"] = children_data.get("total_count", 0)

            children.append(item)

        return {
            "items": children,
            "has_more": has_more,
            "total_count": len(brains)
        }

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

        # Normalize current URL (already clean from data-base-url)
        normalized_current = current_url.rstrip("/")

        # Check if this item is current or parent
        is_current = (item_url == normalized_current)
        is_parent = normalized_current.startswith(item_url + "/")

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
            "title": translate(node.get("Title", ""), to_utf8=False),
            "description": translate(
                node.get("Description", ""), to_utf8=False),
            "url": item_url,
            "icon": icon,
            "review_state": node.get("review_state", ""),
            "is_current": is_current,
            "is_parent": is_parent,
            "is_folderish": node.get("show_children", False),
            "portal_type": node.get("portal_type", ""),
            "depth": node.get("depth", 0),
            "has_more": node.get("has_more", False),
            "total_count": node.get("total_count", 0),
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
