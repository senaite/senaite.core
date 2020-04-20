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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.
from AccessControl import Unauthorized
from Products.CMFCore.permissions import View
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets.navigation import Renderer as BaseRenderer

from bika.lims import api
from bika.lims.api.security import check_permission


class NavigationPortletRenderer(BaseRenderer):
    _template = ViewPageTemplateFile(
        "templates/plone.app.portlets.portlets.navigation.pt")
    recurse = ViewPageTemplateFile(
        "templates/plone.app.portlets.portlets.navigation_recurse.pt")

    def createNavTree(self):
        data = self.getNavTree()

        # We only want the items from the nav tree for which current user has
        # "View" permission granted
        data = self.purge_nav_tree(data)

        bottomLevel = self.data.bottomLevel or self.properties.getProperty('bottomLevel', 0)

        if bottomLevel < 0:
            # Special case where navigation tree depth is negative
            # meaning that the admin does not want the listing to be displayed
            return self.recurse([], level=1, bottomLevel=bottomLevel)
        else:
            return self.recurse(children=data.get('children', []), level=1, bottomLevel=bottomLevel)

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
