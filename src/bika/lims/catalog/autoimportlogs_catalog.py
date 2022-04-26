# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.1.0

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaCatalogAutoImportLogsListing
from zope.interface import implements
from senaite.core.catalog import AUTOIMPORTLOG_CATALOG as CATALOG_AUTOIMPORTLOGS_LISTING  # noqa


class BikaCatalogAutoImportLogsListing(BaseCatalog):
    implements(IBikaCatalogAutoImportLogsListing)


InitializeClass(BikaCatalogAutoImportLogsListing)
