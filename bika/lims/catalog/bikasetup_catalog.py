# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import sys
import traceback
from App.class_init import InitializeClass
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.interfaces import IBikaSetupCatalog
from zope.interface import implements


class BikaSetupCatalog(BikaCatalogTool):
    """
    Catalog for all bika_setup objects
    """
    implements(IBikaSetupCatalog)

    def __init__(self):
        BikaCatalogTool.__init__(self, 'bika_setup_catalog',
                                 'Bika Setup Catalog',
                                 'BikaSetupCatalog')

    def clearFindAndRebuild(self):
        """
        Override parent method to handle both archetypes and dexterity objects
        by finding all appropriate object explicitly and reindexing them
        """
        at = api.get_tool('archetype_tool')

        def is_object_in_catalog(obj):
            if api.is_at_content(obj):
                catalogs = \
                    [c.getId() for c in at.getCatalogsByType(obj.portal_type)]
                return 'bika_setup_catalog' in catalogs

            elif api.is_dexterity_content(obj):
                if hasattr(obj, '_bika_catalogs'):
                    return 'bika_setup_catalog' in obj._bika_catalogs
                else:
                    # Cannot determine is in setup catalog
                    return False

            else:
                # for non-content like tools, plone site, etc
                return False

        def get_catalog_objects(parent):
            objs = []
            if is_object_in_catalog(parent):
                objs = [parent]

            if hasattr(parent, 'objectItems'):
                for (id, obj) in parent.objectItems():
                    objs.extend(get_catalog_objects(obj))

            return objs

        def reindex_object(obj):
            try:
                self.reindexObject(obj)
            except:
                logger.error(traceback.format_exc())
                e = sys.exc_info()
                logger.error(
                    "Unable to clean and rebuild %s due to: %s" % (
                        self.id, e))

        self.manage_catalogClear()
        portal = api.get_portal()

        objects = get_catalog_objects(portal)
        for obj in objects:
            reindex_object(obj)

        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaSetupCatalog)
