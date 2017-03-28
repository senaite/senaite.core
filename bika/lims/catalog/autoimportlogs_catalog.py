# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from zope.interface import implements
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
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
            'allowedRolesAndUsers': 'KeywordIndex',
            'portal_type': 'FieldIndex',
            'UID': 'FieldIndex',
            'getInstrumentUID': 'FieldIndex',
            # allowedRolesAndUsers is obligatory if we are going to
            # run advancedqueries against this catalog.
            'allowedRolesAndUsers': 'KeywordIndex',
        },
        'columns': [
            'UID',
            'getId',
            'meta_type',
            'Title',
            'created',
            'allowedRolesAndUsers',
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


class BikaCatalogAutoImportLogsListing(BikaCatalogTool):
    """
    Catalog for Auto import listings
    """
    implements(IBikaCatalogAutoImportLogsListing)

    def __init__(self):
        BikaCatalogTool.__init__(self, CATALOG_AUTOIMPORTLOGS_LISTING,
                                 'Bika Catalog Auto-Import Logs Listing',
                                 'BikaCatalogAutoImportLogsListing')


InitializeClass(BikaCatalogAutoImportLogsListing)
