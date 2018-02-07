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
        def getObjects(obj):
            objs = [obj]
            if hasattr(obj, 'objectItems'):
                for item in obj.objectItems():
                    objs.extend(getObjects(item[1]))
            return objs

        self.manage_catalogClear()
        portal = api.get_portal()

        start_obj = portal['bika_setup']
        objects = getObjects(start_obj)
        for obj in objects:
            try:
                self.reindexObject(obj)
            except:
                logger.error(traceback.format_exc())
                e = sys.exc_info()
                logger.error(
                    "Unable to clean and rebuild %s due to: %s" % (self.id, e))

        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaSetupCatalog)
