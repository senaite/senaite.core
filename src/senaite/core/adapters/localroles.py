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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

import six
from bika.lims import api
from bika.lims import logger
from bika.lims.utils import get_client
from borg.localrole.default_adapter import DefaultLocalRoleAdapter
from collections import defaultdict
from senaite.core.interfaces import IDynamicLocalRoles
from zope.component import getAdapters
from zope.interface import implementer


class DynamicLocalRoleAdapter(DefaultLocalRoleAdapter):
    """Gives additional Member local roles based on current user and context
    This enables giving additional permissions on items out of the user's
    current traverse path
    """

    _roles_in_context = defaultdict(dict)

    def getRolesInContext(self, context, principal_id):
        """Returns the dynamically calculated 'local' roles for the given
        principal and context
        @param context: context to calculate roles for the given principal
        @param principal_id: User login id
        @return List of dynamically calculated local-roles for user and context
        """
        if not api.is_object(context):
            # We only apply dynamic local roles to valid objects
            return []

        # This function is called a lot within same request, do some cache
        context_uid = api.get_uid(context)
        roles = self._roles_in_context.get(context_uid, {})
        if principal_id in roles:
            return roles.get(principal_id)

        # Look for adapters
        roles = set()
        path = api.get_path(context)
        adapters = getAdapters((context,), IDynamicLocalRoles)
        for name, adapter in adapters:
            local_roles = adapter.getRoles(principal_id)
            logger.info(u"{}::{}::{}: {}".format(name, path, principal_id,
                                                 repr(local_roles)))
            roles.update(local_roles)

        # Store in cache
        self._roles_in_context[context_uid].update({
            principal_id: list(roles)
        })
        return self._roles_in_context[context_uid][principal_id]

    def getRoles(self, principal_id):
        """Returns both non-local and local roles for the given principal in
        current context
        @param principal_id: User login id
        @return: list of non-local and local roles for the user and context
        """
        default_roles = self._rolemap.get(principal_id, [])
        dynamic_roles = self.getRolesInContext(self.context, principal_id)
        return list(set(default_roles + dynamic_roles))

    def getAllRoles(self):
        roles = {}
        # Iterate through all members to extract their dynamic local role for
        # current context
        mtool = api.get_tool("portal_membership")
        for principal_id in mtool.listMemberIds():
            user_roles = self.getRoles(principal_id)
            if user_roles:
                roles.update({principal_id: user_roles})
        return six.iteritems(roles)


@implementer(IDynamicLocalRoles)
class ClientAwareLocalRoles(object):
    """Adapter for the assignment of dynamic local roles to users that are
    linked to a ClientContact for objects that belong to same client
    """

    def __init__(self, context):
        self.context = context

    def getContactPath(self, principal_id):
        """Returns the path of the contact object the principal belongs to
        """
        query = {"portal_type": "Contact", "getUsername": principal_id}
        brains = api.search(query, catalog="portal_catalog")
        if len(brains) != 1:
            return ""
        return api.get_path(brains[0])

    def getRoles(self, principal_id):
        """Returns ["Owner"] local role if the user is linked to a Client
        Contact that belongs to the same client as the current context
        """
        # Get the client of current context, if any
        client = get_client(self.context)
        if not client:
            return []

        # Check if the user belongs to same client as context
        client_path = api.get_path(client)
        user_path = self.getContactPath(principal_id)
        if not user_path.startswith(client_path):
            return []

        return ["Owner"]
