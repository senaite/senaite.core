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
from bika.lims import APIError
from bika.lims import logger
from bika.lims.utils import get_client
from borg.localrole.default_adapter import DefaultLocalRoleAdapter
from plone.memoize.request import cache
from senaite.core.behaviors import IClientShareableBehavior
from senaite.core.interfaces import IDynamicLocalRoles
from zope.component import getAdapters
from zope.interface import implementer


def _request_cache(method, *args):
    """Decorator that ensures the call to the given method with the given
    arguments only takes place once within same request
    """
    # Extract the path of the context from the instance
    try:
        path = api.get_path(args[0].context)
    except APIError:
        path = "no-context"

    return [
        method.__name__,
        path,
        args[1:],
    ]


class DynamicLocalRoleAdapter(DefaultLocalRoleAdapter):
    """Gives additional Member local roles based on current user and context
    This enables giving additional permissions on items out of the user's
    current traverse path
    """

    @property
    def request(self):
        # Fixture for tests that do not have a regular request!!!
        return api.get_request() or api.get_test_request()

    def getRolesInContext(self, context, principal_id):
        """Returns the dynamically calculated 'local' roles for the given
        principal and context
        @param context: context to calculate roles for the given principal
        @param principal_id: User login id
        @return List of dynamically calculated local-roles for user and context
        """
        roles = set()
        path = api.get_path(context)
        adapters = getAdapters((context,), IDynamicLocalRoles)
        for name, adapter in adapters:
            local_roles = adapter.getRoles(principal_id)
            if local_roles:
                logger.debug(u"{}::{}::{}: {}".format(name, path, principal_id,
                                                      repr(local_roles)))
            roles.update(local_roles)
        return list(roles)

    @cache(get_key=_request_cache, get_request='self.request')
    def getRoles(self, principal_id):
        """Returns both non-local and local roles for the given principal in
        current context
        @param principal_id: User login id
        @return: list of non-local and local roles for the user and context
        """
        default_roles = self._rolemap.get(principal_id, [])
        if not api.is_object(self.context):
            # We only apply dynamic local roles to valid objects
            return default_roles[:]

        if principal_id not in self.getMemberIds():
            # We only apply dynamic local roles to existing users
            return default_roles[:]

        # Extend with dynamically computed roles
        dynamic_roles = self.getRolesInContext(self.context, principal_id)
        return list(set(default_roles + dynamic_roles))

    def getAllRoles(self):
        roles = {}
        # Iterate through all members to extract their dynamic local role for
        # current context
        for principal_id in self.getMemberIds():
            user_roles = self.getRoles(principal_id)
            if user_roles:
                roles.update({principal_id: user_roles})
        return six.iteritems(roles)

    @cache(get_key=_request_cache, get_request='self.request')
    def getMemberIds(self):
        """Return the list of user ids
        """
        mtool = api.get_tool("portal_membership")
        return mtool.listMemberIds()


@implementer(IDynamicLocalRoles)
class ClientAwareLocalRoles(object):
    """Adapter for the assignment of dynamic local roles to users that are
    linked to a ClientContact for objects that belong to same client
    """

    def __init__(self, context):
        self.context = context

    def hasContact(self, client, principal_id):
        """Returns whether the client passed in has a contact linked to a user
        with the given principal_id
        """
        query = {
            "portal_type": "Contact",
            "getUsername": principal_id,
            "getParentUID": api.get_uid(client),
        }
        brains = api.search(query, catalog="portal_catalog")
        return len(brains) == 1

    def getRoles(self, principal_id):
        """Returns ["Owner"] local role if the user is linked to a Client
        Contact that belongs to the same client as the current context
        """
        # Get the client of current context, if any
        client = get_client(self.context)
        if not client:
            return []

        # Check if the user belongs to same client as context
        if not self.hasContact(client, principal_id):
            return []

        return ["Owner"]


@implementer(IDynamicLocalRoles)
class ClientShareableLocalRoles(object):
    """Adapter for the assignment of roles for content shared across clients
    """

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal_id):
        """Returns ["ClientGuest"] local role if the current context is
        shareable across clients and the user for the principal_id belongs to
        one of the clients for which the context can be shared
        """
        # Get the clients this context is shared with
        behavior = IClientShareableBehavior(self.context)
        clients = filter(api.is_uid, behavior.getRawClients())
        if not clients:
            return []

        # Check if the user belongs to at least one of the clients
        # this context is shared with
        query = {
            "portal_type": "Contact",
            "getUsername": principal_id,
            "getParentUID": clients,
        }
        brains = api.search(query, catalog="portal_catalog")
        if len(brains) == 0:
            return []

        return ["ClientGuest"]
