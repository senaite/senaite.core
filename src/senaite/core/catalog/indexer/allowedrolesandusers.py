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
from plone.indexer import indexer
from senaite.core import logger
from senaite.core.interfaces import IClientAwareMixin
from Products.CMFPlone.CatalogTool import \
    allowedRolesAndUsers as base_indexer_factory


CLIENT_TOKEN_PREFIX = "client:"


def _get_client_uid(instance):
    """Return the UID of the client this instance belongs to, if any."""
    if IClient.providedBy(instance):
        return api.get_uid(instance)
    getter = getattr(instance, "getClientUID", None)
    if getter is None:
        return ""
    try:
        return getter() or ""
    except Exception as exc:
        # A broken `getClientUID` would silently strip every
        # `client:<uid>` token at next reindex, so log loud
        # enough that the cause is traceable while keeping
        # the catalog write itself non-fatal.
        logger.debug(
            "getClientUID failed on %r: %s" % (instance, exc))
        return ""


def _augment(instance):
    """Return base allowedRolesAndUsers tokens augmented with the
    `client:<uid>` token for client-tree content.

    The base indexer (`Products.CMFPlone.CatalogTool`) already records
    `user:<id>` and `user:<group_id>` tokens from local roles. We add a
    stable `client:<uid>` token that is bound to the client identity,
    so the catalog never needs to be re-indexed when a contact link is
    added or removed; the corresponding token is injected into the
    catalog query for the asking user via
    `BaseCatalog._listAllowedRolesAndUsers`.
    """
    # `base_indexer_factory` is a `DelegatingIndexerFactory` (see
    # plone.indexer.decorator). The underlying function is on
    # `.callable` and computes the standard token list.
    base = list(base_indexer_factory.callable(instance))
    client_uid = _get_client_uid(instance)
    if client_uid:
        base.append(CLIENT_TOKEN_PREFIX + client_uid)
    return base


@indexer(IClient)
def allowedRolesAndUsers_for_client(instance):
    return _augment(instance)


@indexer(IClientAwareMixin)
def allowedRolesAndUsers_for_client_aware(instance):
    return _augment(instance)
