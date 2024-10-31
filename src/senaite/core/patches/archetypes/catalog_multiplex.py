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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from Products.Archetypes.Referenceable import Referenceable
from Products.Archetypes.utils import shasattr
from senaite.core.catalog import AUDITLOG_CATALOG


def is_auditlog_enabled():
    setup = api.get_senaite_setup()
    if not setup:
        return False
    return setup.getEnableGlobalAuditlog()


def indexObject(self):
    """Handle indexing for AT based objects
    """
    # Never index temporary AT objects
    if api.is_temporary(self):
        return

    # get all registered catalogs
    catalogs = api.get_catalogs_for(self)

    for catalog in catalogs:
        # skip auditlog_catalog if global auditlogging is deactivated
        if catalog.id == AUDITLOG_CATALOG and not is_auditlog_enabled():
            continue
        # always use catalog tool queuing system
        catalog.indexObject(self)


def unindexObject(self):
    """Handle unindexing for AT based objects
    """
    # Never unindex temporary AT objects
    if api.is_temporary(self):
        return

    # get all registered catalogs
    catalogs = api.get_catalogs_for(self)

    for catalog in catalogs:
        # skip auditlog_catalog if global auditlogging is deactivated
        if catalog.id == AUDITLOG_CATALOG and not is_auditlog_enabled():
            continue
        # always use catalog tool queuing system
        catalog.unindexObject(self)


def reindexObject(self, idxs=None):
    """Reindex all AT based contents with the catalog queuing system
    """
    # Never reindex temporary AT objects
    if api.is_temporary(self):
        return

    if idxs is None:
        idxs = []

    # Copy (w/o knowig if this is required of not x_X)
    if idxs == [] and shasattr(self, "notifyModified"):
        # Archetypes default setup has this defined in ExtensibleMetadata
        # mixin. note: this refreshes the 'etag ' too.
        self.notifyModified()
    self.http__refreshEtag()
    # /Paste

    catalogs = api.get_catalogs_for(self)

    for catalog in catalogs:
        # skip auditlog_catalog if global auditlogging is deactivated
        if catalog.id == AUDITLOG_CATALOG and not is_auditlog_enabled():
            continue
        # We want the intersection of the catalogs idxs
        # and the incoming list.
        lst = idxs
        indexes = catalog.indexes()
        if idxs:
            lst = [i for i in idxs if i in indexes]
        # use catalog tool queuing system
        catalog.reindexObject(self, idxs=lst)

    # Copy (w/o knowig if this is required of not x_X)
    #
    # We only make this call if idxs is not passed.
    #
    # manage_afterAdd/manage_beforeDelete from Referenceable take
    # care of most of the issues, but some places still expect to
    # call reindexObject and have the uid_catalog updated.
    # TODO: fix this so we can remove the following lines.
    if not idxs:
        if isinstance(self, Referenceable):
            isCopy = getattr(self, '_v_is_cp', None)
            if isCopy is None:
                self._catalogUID(self)
    # /Paste
