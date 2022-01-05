# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.1.0

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing
from zope.interface import implements
from senaite.core.catalog import SAMPLE_CATALOG as CATALOG_ANALYSIS_REQUEST_LISTING  # noqa


class BikaCatalogAnalysisRequestListing(BaseCatalog):
    implements(IBikaCatalogAnalysisRequestListing)


InitializeClass(BikaCatalogAnalysisRequestListing)
