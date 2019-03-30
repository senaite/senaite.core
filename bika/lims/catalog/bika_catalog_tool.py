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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import sys
import traceback
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
import transaction
from bika.lims import logger


class BikaCatalogTool(CatalogTool):
    """
    Base class for Bika CatalogTool types, that provides common functions for
    them, like clearFindAndRebuild
    """
    security = ClassSecurityInfo()
    _properties = ({'id': 'title', 'type': 'string', 'mode': 'w'},)
    plone_tool = 1

    def __init__(self, id, title, portal_meta_type):
        self.portal_type = portal_meta_type
        self.meta_type = portal_meta_type
        self.title = title
        self.counter = None
        ZCatalog.__init__(self, id)

    def clearFindAndRebuild(self):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with an indexObject method), and reindexes them.
           This may take a long time.
        """
        def indexObject(obj, path):
            self.reindexObject(obj)
            self.counter += 1
            if self.counter % 100 == 0:
                logger.info('Progress: {} objects have been cataloged for {}.'
                            .format(self.counter, self.id))

        logger.info('Cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]
            self.counter = 0
            self.manage_catalogClear()
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal.ZopeFindAndApply(portal,
                                    obj_metatypes=types,
                                    search_sub=True,
                                    apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')


    def softClearFindAndRebuild(self):
        """
            Empties catalog, then finds all contentish objects quering over
            uid_catalog and reindexes them.
            This may take a long time and will not care about missing
            objects in uid_catalog.
        """
        logger.info('Soft cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]
            self.counter = 0
            self.manage_catalogClear()
            # Getting UID catalog
            portal = getToolByName(self, 'portal_url').getPortalObject()
            uid_c = getToolByName(portal, 'uid_catalog')
            brains = uid_c(portal_type=types)
            self.total = len(brains)
            for brain in brains:
                obj = brain.getObject()
                self.catalog_object(
                    obj, idxs=self.indexes(),
                    update_metadata=True)
                self.counter += 1
                if self.counter % 100 == 0:
                    logger.info(
                        'Progress: {}/{} objects have been cataloged for {}.'
                            .format(self.counter, self.total, self.id))
                    if self.counter % 1000 == 0:
                        transaction.commit()
                        logger.info(
                            '{0} items processed.'
                                .format(self.counter))
            transaction.commit()
            logger.info(
                '{0} items processed.'
                    .format(self.counter))
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)

    security.declareProtected(ManagePortal, 'softClearFindAndRebuild')
