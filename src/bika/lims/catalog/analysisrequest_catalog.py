# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.0.1

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing
from zope.interface import implements


class BikaCatalogAnalysisRequestListing(BaseCatalog):
    implements(IBikaCatalogAnalysisRequestListing)


InitializeClass(BikaCatalogAnalysisRequestListing)
