# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.usergroups_groupsoverview import \
    GroupsOverviewControlPanel as BaseView
from senaite.core.config.roles import HIDDEN_ROLES


class GroupsOverviewControlPanel(BaseView):
    """Custom userprefs controlpanel
    """

    @property
    def portal_roles(self):
        """Return only SENAITE Roles
        """
        pmemb = getToolByName(aq_inner(self.context), "portal_membership")
        roles = pmemb.getPortalRoles()
        return filter(lambda r: r not in HIDDEN_ROLES, roles)
