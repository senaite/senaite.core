# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.1.0

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaCatalog
from zope.interface import implements
from senaite.core.catalog import SENAITE_CATALOG as BIKA_CATALOG  # noqa


class BikaCatalog(BaseCatalog):
    implements(IBikaCatalog)


InitializeClass(BikaCatalog)
