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

import six
from Acquisition import aq_inner
from bika.lims import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.usergroups_usersoverview import \
    UsersOverviewControlPanel as BaseView
from senaite.core.catalog import CLIENT_CATALOG
from senaite.core.config.roles import HIDDEN_ROLES
from zExceptions import Forbidden


class UsersOverviewControlPanel(BaseView):
    """Custom userprefs controlpanel
    """

    @property
    def portal_roles(self):
        """Return only SENAITE Roles
        """
        pmemb = getToolByName(aq_inner(self.context), "portal_membership")
        roles = pmemb.getPortalRoles()
        return filter(lambda r: r not in HIDDEN_ROLES, roles)

    def get_clients(self):
        """Return all clients from the site
        """
        query = {"portal_type": "Client"}
        clients = api.search(query, CLIENT_CATALOG)
        return list(map(api.get_object, clients))

    def deleteMembers(self, member_ids):
        # this method exists to bypass the 'Manage Users' permission check
        # in the CMF member tool's version
        context = aq_inner(self.context)
        mtool = api.get_tool("portal_membership")

        # Delete members in acl_users.
        acl_users = context.acl_users
        if isinstance(member_ids, six.string_types):
            member_ids = (member_ids,)
        member_ids = list(member_ids)
        for member_id in member_ids[:]:
            member = mtool.getMemberById(member_id)
            if member is None:
                member_ids.remove(member_id)
            else:
                if not member.canDelete():
                    raise Forbidden
                if "Manager" in member.getRoles() and not self.is_zope_manager:
                    raise Forbidden
        try:
            acl_users.userFolderDelUsers(member_ids)
        except (AttributeError, NotImplementedError):
            raise NotImplementedError('The underlying User Folder '
                                      'doesn\'t support deleting members.')

        # Delete member data in portal_memberdata.
        mdtool = api.get_tool("portal_memberdata")
        if mdtool is not None:
            for member_id in member_ids:
                mdtool.deleteMemberData(member_id)

        # NOTE: the original call below iterates over **all** objects
        # recursively to remove the local roles, which takes ages!
        # The only place we allow local roles to be assigned are clients.
        # Therefore, we want to make sure to remove them just from there
        #
        # Delete members' local roles.
        # mtool.deleteLocalRoles(
        #     getUtility(ISiteRoot),
        #     member_ids,
        #     reindex=1,
        #     recursive=1
        # )
        for client in self.get_clients():
            mtool.deleteLocalRoles(client, member_ids, reindex=0, recursive=0)
