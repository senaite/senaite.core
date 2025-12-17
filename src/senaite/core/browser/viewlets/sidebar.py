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

from Acquisition import aq_chain
from Acquisition import aq_inner
from bika.lims import api
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.portlets.portlets import navigation
from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INavigationSchema
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core import logger
from zope.component import getMultiAdapter
from zope.component import getUtility


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
        # Cache portal_types tool for efficient icon lookups
        self._portal_types = None

    @property
    def portal_types(self):
        """Cached portal_types tool"""
        if self._portal_types is None:
            self._portal_types = api.get_tool("portal_types")
        return self._portal_types

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
        # Get context - use navigation root, not current context
        context = aq_inner(self.context)

        # Get the navigation root (usually the Plone site root)
        portal_state = getMultiAdapter(
            (context, self.request),
            name="plone_portal_state"
        )
        navigation_root = portal_state.navigation_root()

        # Read navigation settings from registry (configured in control panel)
        registry = getUtility(IRegistry)
        nav_settings = registry.forInterface(
            INavigationSchema,
            prefix="plone",
            check=False
        )

        # Get navigation depth from registry
        navigation_depth = getattr(nav_settings, "navigation_depth", 3)

        # Get displayed types
        displayed_types = tuple(getattr(
            nav_settings, "displayed_types", []))

        # Build tree using uid_catalog
        data = self._build_tree_from_uid_catalog(
            navigation_root,
            navigation_depth,
            displayed_types
        )

        # Process into JSON-friendly format
        return self._process_navigation_tree(data, current_url)

    def _enhance_with_acquisition_chain(
            self, tree_data, current_url, navigation_root, nav_settings):
        """Enhance navigation tree with acquisition chain from current context

        SENAITE uses specialized catalogs (senaite_catalog_client,
        senaite_catalog_sample, etc.) so items won't appear in portal_catalog.
        This method traverses the acquisition chain and inserts parent objects
        into the tree to show the current path.

        :param tree_data: Navigation tree dict from buildFolderTree
        :param current_url: URL of current page
        :param navigation_root: The navigation root object
        :param nav_settings: Navigation settings from registry
        """

        if not tree_data or not current_url:
            return

        try:
            # Get displayed types from settings
            displayed_types = list(getattr(
                nav_settings, "displayed_types", []))
            navigation_depth = getattr(nav_settings, "navigation_depth", 3)

            # Get the root path for depth calculation
            root_path = navigation_root.getPhysicalPath()
            root_depth = len(root_path)
            max_depth = root_depth + navigation_depth

            # Parse current URL to get path
            # Remove protocol, domain, and query string
            url_path = current_url.split("?")[0].split("#")[0]
            if "//" in url_path:
                url_path = "/" + url_path.split("//", 1)[1].split("/", 1)[1]

            # Get object at this path
            try:
                current_obj = self.context.restrictedTraverse(
                    str(url_path.lstrip("/")))
            except Exception:
                # Could not traverse to this path, skip enhancement
                return

            # Traverse up acquisition chain
            chain_items = []
            for obj in aq_chain(current_obj):
                # Stop at navigation root
                if obj == navigation_root:
                    break

                # Check if this object should be in navigation
                portal_type = getattr(obj, "portal_type", None)
                if not portal_type or portal_type not in displayed_types:
                    continue

                # Check depth
                obj_path = obj.getPhysicalPath()
                obj_depth = len(obj_path)
                if obj_depth > max_depth:
                    continue

                # Get object info
                try:
                    chain_items.append({
                        "id": obj.getId(),
                        "Title": obj.Title(),
                        "Description": obj.Description() if hasattr(
                            obj, "Description") else "",
                        "getURL": obj.absolute_url(),
                        "portal_type": portal_type,
                        "path": "/".join(obj_path),
                        "depth": obj_depth - root_depth,
                        "review_state": api.get_review_status(obj),
                        "show_children": True,
                        "item": obj,
                        "children": []
                    })
                except Exception as e:
                    logger.warning(
                        "Error processing acquisition chain item: %s" % str(e))
                    continue

            # Insert chain items into tree
            if chain_items:
                self._insert_chain_into_tree(
                    tree_data, chain_items, displayed_types)

        except Exception as e:
            logger.error(
                "Error enhancing navigation with acquisition chain: %s" %
                str(e), exc_info=True)

    def _insert_chain_into_tree(self, tree_data, chain_items, displayed_types):
        """Insert acquisition chain items into the navigation tree

        :param tree_data: Navigation tree dict
        :param chain_items: List of items from acquisition chain (child to parent order)
        :param displayed_types: List of types to display
        """
        if not chain_items:
            return

        # Reverse to go from parent to child
        chain_items.reverse()

        # Start at root children
        current_level = tree_data.get("children", [])

        # For each item in chain, find or create its place in tree
        for i, chain_item in enumerate(chain_items):
            item_path = chain_item["path"]

            # Look for this item in current level
            found = False
            for existing_item in current_level:
                existing_brain = existing_item.get("item")
                if existing_brain:
                    # Item is a catalog brain, use getPath() method
                    existing_path_str = existing_brain.getPath()
                    if existing_path_str == item_path:
                        # Found it, move to its children for next iteration
                        current_level = existing_item.get("children", [])
                        found = True
                        break

            # If not found, insert it
            if not found:
                # Find parent in current level
                parent_path = "/".join(item_path.split("/")[:-1])
                inserted = False

                for existing_item in current_level:
                    existing_brain = existing_item.get("item")
                    if existing_brain:
                        # Item is a catalog brain, use getPath() method
                        existing_path_str = existing_brain.getPath()
                        if existing_path_str == parent_path:
                            # Add as child of this item
                            existing_item.setdefault("children", [])
                            existing_item["children"].append(chain_item)
                            current_level = existing_item["children"]
                            inserted = True
                            break

                if not inserted:
                    # Parent not found, this shouldn't happen but log it
                    logger.warning(
                        "Could not find parent for chain item: %s" %
                        str(chain_item["Title"]))
                    break

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
        normalized_current = current_url.rstrip("/")

        # Check if this item is current or parent
        is_current = (item_url == normalized_current)
        is_parent = (
            normalized_current.startswith(item_url + "/")
            if item_url else False
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
