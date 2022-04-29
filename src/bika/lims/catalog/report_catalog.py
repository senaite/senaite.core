# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.1.0

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaCatalogReport
from zope.interface import implements
from senaite.core.catalog import REPORT_CATALOG as CATALOG_REPORT_LISTING  # noqa


class BikaCatalogReport(BaseCatalog):
    implements(IBikaCatalogReport)


InitializeClass(BikaCatalogReport)
