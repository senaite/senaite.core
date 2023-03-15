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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from plone.indexer.interfaces import IIndexableObject
from Products.ZCatalog.ZCatalog import ZCatalog
from senaite.core.catalog import AUDITLOG_CATALOG
from zope.component import queryMultiAdapter


def is_auditlog_enabled():
    setup = api.get_senaite_setup()
    if not setup:
        return False
    return setup.getEnableGlobalAuditlog()


def catalog_object(self, object, uid=None, idxs=None,
                   update_metadata=1, pghandler=None):

    # Never catalog temporary objects
    if api.is_temporary(object):
        return

    # skip indexing auditlog catalog if disabled
    if self.id == AUDITLOG_CATALOG:
        if not is_auditlog_enabled():
            return

    if idxs is None:
        idxs = []
    self._increment_counter()

    w = object
    if not IIndexableObject.providedBy(object):
        # This is the CMF 2.2 compatible approach, which should be used
        # going forward
        wrapper = queryMultiAdapter((object, self), IIndexableObject)
        if wrapper is not None:
            w = wrapper

    ZCatalog.catalog_object(self, w, uid, idxs,
                            update_metadata, pghandler=pghandler)
