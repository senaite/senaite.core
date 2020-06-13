# -*- coding: utf-8 -*-

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
