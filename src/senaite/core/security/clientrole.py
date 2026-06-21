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

from bika.lims import api
from bika.lims.interfaces import IClient
from borg.localrole.interfaces import ILocalRoleProvider
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from senaite.core import logger
from senaite.core.interfaces import IClientAwareMixin
from zope.component import adapter
from zope.interface import implementer

LINKED_CLIENT_UID_PROPERTY = "linked_client_uid"
# Owner gives broad read/edit access on the client tree (matches the
# legacy local-role grant). Client gives the SENAITE-specific
# per-field edit permissions on Sample (Date Sampled, Sample Type,
# Client Order Number, …) and `senaite.core: View Navigation`, none
# of which are covered by Owner. Granting both here makes Client a
# dynamic, contextual role that is never assigned globally.
GRANTED_ROLES = ("Owner", "Client")


def _get_context_client_uid(context):
    """Return the UID of the client the context belongs to, if any."""
    if IClient.providedBy(context):
        return api.get_uid(context)
    getter = getattr(context, "getClientUID", None)
    if getter is None:
        return ""
    try:
        return getter() or ""
    except Exception as exc:
        # A broken `getClientUID` would silently revoke Owner from
        # every linked client user on this context. Log at debug
        # so the failure is traceable.
        logger.debug(
            "getClientUID failed on %r: %s" % (context, exc))
        return ""


def _get_linked_client_uid(context, principal_id):
    """Return the `linked_client_uid` member property for the
    given principal, or an empty string.

    Shared by the per-context and the site-root role providers.
    Returns "" on every soft failure (missing acl_users, unknown
    principal, missing property, broken plugin) and logs the
    exception at debug.
    """
    if not principal_id:
        return ""
    acl_users = getToolByName(context, "acl_users", None)
    if acl_users is None:
        return ""
    user = acl_users.getUserById(principal_id)
    if user is None:
        return ""
    try:
        return user.getProperty(LINKED_CLIENT_UID_PROPERTY, "") or ""
    except Exception as exc:
        logger.debug(
            "linked_client_uid lookup failed on user %r: %s"
            % (user, exc))
        return ""


@implementer(ILocalRoleProvider)
@adapter(IClientAwareMixin)
class ClientLinkRoleProvider(object):
    """Dynamic local-role provider granting Owner on the client tree.

    Grants the ``Owner`` role to a principal when the principal's
    ``linked_client_uid`` member property matches the UID of the
    client that contains (or owns through a reference) the adapted
    context. This replaces the legacy "per-client group with a
    persisted Owner local role" mechanism: no group exists, no
    ``__ac_local_roles__`` are written on the client folder, and no
    recursive ``reindexObjectSecurity`` is ever needed when a contact
    is linked to a user.

    The provider intentionally returns an empty iterator from
    ``getAllRoles``. ``getAllRoles`` is called only when something
    needs to enumerate every principal with a role on this context
    (notably the Plone catalog indexer for
    ``allowedRolesAndUsers``). Reporting roles here would force a
    catalog reindex of every client-tree object on every contact
    link/unlink. Instead, the catalog carries a stable
    ``client:<uid>`` token (see
    ``senaite.core.catalog.indexer.allowedrolesandusers``) and the
    matching token is injected into the catalog query for the asking
    user by ``BaseCatalog._listAllowedRolesAndUsers``.

    ``getRoles`` is the per-principal lookup used during traversal
    and permission checks; it is O(1) (a member-property read on the
    user object) and fires only for the asking user.
    """

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal_id):
        linked_client_uid = _get_linked_client_uid(
            self.context, principal_id)
        if not linked_client_uid:
            return ()
        if _get_context_client_uid(self.context) == linked_client_uid:
            return GRANTED_ROLES
        return ()

    def getAllRoles(self):
        return iter(())


@implementer(ILocalRoleProvider)
@adapter(IClient)
class ClientRoleProvider(ClientLinkRoleProvider):
    """Same dynamic Owner grant for the Client folder itself."""


@implementer(ILocalRoleProvider)
@adapter(ISiteRoot)
class GlobalClientRoleProvider(object):
    """Grant the global `Client` role to users with `linked_client_uid`.

    Restores the global `Client` role that linked client users used to
    receive via membership in the per-client group (which carried
    ``roles=["Client"]``). Without it, permission checks performed at
    the site root, such as the sidebar's `View Navigation` check in
    ``senaite.core.browser.viewlets.sidebar.SidebarViewletManager``,
    fail for client users because the per-context providers above only
    fire on the client tree.

    Local-role acquisition propagates the grant from the site root to
    every descendant, so this single registration covers every
    permission check anywhere in the site without re-introducing a
    persistent group.

    `getAllRoles` returns empty for the same reason as on the client
    tree: enumerating every linked user would force a catalog reindex
    on every link/unlink. Catalog filtering keeps using the
    `client:<uid>` token injected by
    ``BaseCatalog._listAllowedRolesAndUsers``; this provider exists
    only to satisfy runtime permission checks that walk
    ``user.getRolesInContext``.
    """

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal_id):
        linked = _get_linked_client_uid(self.context, principal_id)
        return ("Client",) if linked else ()

    def getAllRoles(self):
        return iter(())
