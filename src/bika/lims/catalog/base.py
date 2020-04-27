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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import transaction
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import \
    manage_zcatalog_entries as ManageZCatalogEntries
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.class_init import InitializeClass
from bika.lims import api
from bika.lims import logger
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.ZCatalog.ZCatalog import ZCatalog


class BaseCatalog(CatalogTool):
    """Base class for specialized catalogs
    """

    security = ClassSecurityInfo()

    def __init__(self, id, title, portal_meta_type):
        self.portal_type = portal_meta_type
        self.meta_type = portal_meta_type
        self.title = title
        self.counter = 0
        ZCatalog.__init__(self, id)

    def get_mapped_types(self):
        """Returns the mapped types for this catalog
        """
        pt = api.get_tool("portal_types")
        at = api.get_tool("archetype_tool")

        # Get all Archetypes which are mapped to this catalog
        at_types = [k for k, v in at.catalog_map.items() if self.id in v]

        # TODO: Discover the mapped catalogs for Dexterity types
        dx_ftis = filter(lambda fti: IDexterityFTI.providedBy(fti),
                         pt.listTypeInfo())
        dx_types = map(lambda fti: fti.getId(), dx_ftis)

        return at_types + dx_types

    def get_portal_type(self, obj):
        """Returns the portal type of the object
        """
        if not api.is_object(obj):
            return None
        return api.get_portal_type(obj)

    def is_indexable(self, obj):
        """Checks if the object can be indexed
        """
        if not (base_hasattr(obj, "reindexObject")):
            return False
        if not (safe_callable(obj.reindexObject)):
            return False
        return True

    @security.protected(ManageZCatalogEntries)
    def clearFindAndRebuild(self):
        # Empties catalog, then finds all contentish objects (i.e. objects
        # with an indexObject method), and reindexes them.
        # This may take a long time.

        # The Catalog ID
        cid = self.getId()

        # The catalog indexes
        idxs = list(self.indexes())

        # Types to consider for this catalog
        obj_metatypes = self.get_mapped_types()

        def indexObject(obj, path):
            __traceback_info__ = path

            # skip non-indexable types
            if not self.is_indexable(obj):
                return

            # skip types that are not mapped to this catalog
            if self.get_portal_type(obj) not in obj_metatypes:
                return

            self.counter += 1

            try:
                obj.reindexObject(idxs=idxs)
            except TypeError:
                # Catalogs have 'indexObject' as well, but they
                # take different args, and will fail
                pass

            if self.counter % 100 == 0:
                logger.info("Progress: {} objects have been cataloged for {}."
                            .format(self.counter, cid))
                transaction.savepoint(optimistic=True)

        logger.info("Cleaning and rebuilding catalog '{}'...".format(cid))
        self.counter = 0
        self.manage_catalogClear()
        portal = aq_parent(aq_inner(self))
        portal.ZopeFindAndApply(
            portal,
            search_sub=True,
            apply_func=indexObject)
        logger.info("Catalog '{}' cleaned and rebuilt".format(cid))


InitializeClass(BaseCatalog)
