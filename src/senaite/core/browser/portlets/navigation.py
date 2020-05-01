# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from bika.lims.api.security import check_permission
from plone.app.portlets.portlets.navigation import Renderer as BaseRenderer
from Products.CMFCore.permissions import View
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NavigationPortletRenderer(BaseRenderer):
    _template = ViewPageTemplateFile("templates/navigation.pt")
    recurse = ViewPageTemplateFile("templates/navigation_recurse.pt")

    def createNavTree(self):
        data = self.getNavTree()

        # We only want the items from the nav tree for which current user has
        # "View" permission granted
        data = self.purge_nav_tree(data)

        bottomLevel = self.data.bottomLevel or 0

        if bottomLevel < 0:
            # Special case where navigation tree depth is negative
            # meaning that the admin does not want the listing to be displayed
            return self.recurse([], level=1, bottomLevel=bottomLevel)
        else:
            return self.recurse(children=data.get("children", []),
                                level=1, bottomLevel=bottomLevel)

    def purge_nav_tree(self, data):
        """Purges the items of the nav tree for which the current user does not
        have "View" permission granted
        """
        item = data.get("item", "")
        if item:
            # Check if current user has "View" permission granted
            try:
                if not check_permission(View, item):
                    return None
            except Unauthorized:
                return None

        if "children" in data:
            children = map(self.purge_nav_tree, data["children"])
            children = filter(None, children)
            data["children"] = children

        return data
