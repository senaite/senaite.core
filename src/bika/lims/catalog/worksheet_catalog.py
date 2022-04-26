# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.1.0

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaCatalogWorksheetListing
from zope.interface import implements
from senaite.core.catalog import WORKSHEET_CATALOG as CATALOG_WORKSHEET_LISTING  # noqa


class BikaCatalogWorksheetListing(BaseCatalog):
    implements(IBikaCatalogWorksheetListing)


InitializeClass(BikaCatalogWorksheetListing)
