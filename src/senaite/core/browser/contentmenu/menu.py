# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from plone.app.contentmenu.menu import \
    DisplaySubMenuItem as BaseDisplaySubMenuItem
from plone.app.contentmenu.menu import \
    FactoriesSubMenuItem as BaseFactoriesSubMenuItem
from plone.app.contentmenu.menu import \
    PortletManagerSubMenuItem as BasePortletManagerSubMenuItem
from plone.app.contentmenu.menu import \
    WorkflowSubMenuItem as BaseWorkflowSubMenuItem
from plone.memoize.instance import memoize
from plone.portlets.interfaces import ILocalPortletAssignable
from senaite.core.interfaces import IShowDisplayMenu
from senaite.core.interfaces import IShowFactoriesMenu


class DisplaySubMenuItem(BaseDisplaySubMenuItem):
    """The "Display" Menu
    """
    @memoize
    def available(self):
        return IShowDisplayMenu.providedBy(self.context)


class FactoriesSubMenuItem(BaseFactoriesSubMenuItem):
    """The "Add" Menu
    """
    @memoize
    def available(self):
        return IShowFactoriesMenu.providedBy(self.context)


class PortletManagerSubMenuItem(BasePortletManagerSubMenuItem):
    """The "Manage Portlets" Menu
    """
    @memoize
    def available(self):
        secman = getSecurityManager()
        has_manage_portlets_permission = secman.checkPermission(
            "Manage portal",
            self.context
        )
        if not has_manage_portlets_permission:
            return False
        else:
            return ILocalPortletAssignable.providedBy(self.context)


class WorkflowSubMenuItem(BaseWorkflowSubMenuItem):
    """The Workflow Menu
    """

    def available(self):
        return super(WorkflowSubMenuItem, self).available()
