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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.contentmenu.view import ContentMenuProvider as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.interfaces import IHideActionsMenu
from zope.browsermenu.interfaces import IBrowserMenu
from zope.component import getUtility


class ContentMenuProvider(Base):
    """Content menu provider for the "view" tab: displays the menu
    """
    index = ViewPageTemplateFile('templates/contentmenu.pt')

    def available(self):
        if IHideActionsMenu.providedBy(self.context):
            return False
        return True

    def fiddle_menu_item(self, item):
        """A helper to  process the menu items before rendering

        Unfortunately, this can not be done more elegant w/o overrides.zcml.
        https://stackoverflow.com/questions/11904155/disable-advanced-in-workflow-status-menu-in-plone
        """
        action = item.get("action")
        if action.endswith("content_status_history"):
            # remove the "Advanced ..." submenu
            submenu = filter(
                lambda m: m.get("title") != "label_advanced",
                item.get("submenu", []) or [])
            item["submenu"] = submenu
        return item

    def menu(self):
        menu = getUtility(IBrowserMenu, name="plone_contentmenu")
        items = menu.getMenuItems(self.context, self.request)
        return map(self.fiddle_menu_item, items)
