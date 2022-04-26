# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.1.0

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaAnalysisCatalog
from zope.interface import implements
from senaite.core.catalog import ANALYSIS_CATALOG as CATALOG_ANALYSIS_LISTING  # noqa


class BikaAnalysisCatalog(BaseCatalog):
    implements(IBikaAnalysisCatalog)


InitializeClass(BikaAnalysisCatalog)
