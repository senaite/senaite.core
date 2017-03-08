# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import sys
import traceback
import transaction
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
# Bika LIMS imports
from bika.lims import logger
from bika.lims.interfaces import IBikaCatalogAutoImportLogsListing


# Using a variable to avoid plain strings in code
CATALOG_AUTOIMPORTLOGS_LISTING = 'bika_catalog_autoimportlogs_listing'

bika_catalog_autoimportlogs_listing_definition = {
    CATALOG_AUTOIMPORTLOGS_LISTING: {
        'types':   ['AutoImportLog', ],
        'indexes': {
            # Minimum indexes for bika_listing
            'id': 'FieldIndex',
            'getId': 'FieldIndex',
            # Necessary to avoid reindexing whole catalog when we need to
            # reindex only one object. ExtendedPathIndex also could be used.
            'path': 'PathIndex',
            'created': 'DateIndex',
            'portal_type': 'FieldIndex',
            'UID': 'FieldIndex',
            'getInstrumentUID': 'FieldIndex'
        },
        'columns': [
            'UID',
            'getId',
            'Title',
            'created',
            'review_state',
            'getObjectWorkflowStates',
            'getInstrumentUrl',
            'getInstrumentTitle',
            'getImportedFile',
            'getInterface',
            'getResults',
            'getLogTime'
        ]
    }
}


class BikaCatalogAutoImportLogsListing(CatalogTool):
    """
    Catalog to list auto-import logs in BikaListing
    """
    implements(IBikaCatalogAutoImportLogsListing)
    title = 'Bika Catalog Auto-Import Logs Listing'
    id = CATALOG_AUTOIMPORTLOGS_LISTING
    portal_type = meta_type = 'BikaCatalogAutoImportLogsListing'
    plone_tool = 1
    security = ClassSecurityInfo()
    _properties = (
      {'id': 'title', 'type': 'string', 'mode': 'w'},)

    def __init__(self):
        ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')

    def clearFindAndRebuild(self):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with an indexObject method), and reindexes them.
           This may take a long time.
        """
        def indexObject(obj, path):
            self.reindexObject(obj)
            transaction.commit()
        logger.info('Cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]
            self.manage_catalogClear()
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal.ZopeFindAndApply(
                portal,
                obj_metatypes=types,
                search_sub=True,
                apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaCatalogAutoImportLogsListing)
