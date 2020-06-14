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

from plone.app.contentmenu.menu import WorkflowMenu as BaseClass
from plone.app.contentmenu.view import ContentMenuProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.interfaces import IHideActionsMenu
from zope.component import getUtility
from zope.browsermenu.interfaces import IBrowserMenu


class SenaiteContentMenuProvider(ContentMenuProvider):
    """Provides a proper styled content menu
    """
    index = ViewPageTemplateFile(
        "templates/plone.app.contentmenu.contentmenu.pt")

    def render(self):
        return self.index()

    # From IContentMenuView

    def available(self):
        if IHideActionsMenu.providedBy(self.context):
            return False
        return True

    def menu(self):
        menu = getUtility(IBrowserMenu, name="plone_contentmenu")
        items = menu.getMenuItems(self.context, self.request)
        # always filter out the selection of the default view
        items = filter(
            lambda a: not a["action"].endswith("/select_default_view"), items)
        items.reverse()
        return items


class WorkflowMenu(BaseClass):
    def getMenuItems(self, context, request):
        """Overrides the workflow actions menu displayed top right in the
        object's view. Displays the current state of the object, as well as a
        list with the actions that can be performed.
        The option "Advanced.." is not displayed and the list is populated with
        all allowed transitions for the object.
        """
        actions = super(WorkflowMenu, self).getMenuItems(context, request)
        # Remove status history menu item ('Advanced...')
        return filter(
            lambda a: not a["action"].endswith("/content_status_history"),
            actions)
