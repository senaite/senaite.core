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
        Override parent method to handle dexterity objects by passing
        ALL oject ids to ZopeFindAndApply
        """
        def getObjectIds(obj):
            obj_ids = [obj.getId()]
            if hasattr(obj, 'objectItems'):
                for item in obj.objectItems():
                    obj_ids.extend(getObjectIds(item[1]))
            return obj_ids

        def indexObject(obj, path):
            self.reindexObject(obj)

        try:
            self.manage_catalogClear()
            portal = api.get_portal()

            object_ids = getObjectIds(portal['bika_setup'])
            portal.ZopeFindAndApply(portal,
                                    obj_ids=object_ids,
                                    search_sub=True,
                                    apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))

        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaSetupCatalog)
