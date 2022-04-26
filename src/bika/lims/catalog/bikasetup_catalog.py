# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.1.0

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaSetupCatalog
from zope.interface import implements
from senaite.core.catalog import SETUP_CATALOG  # noqa
from senaite.core.catalog import SETUP_CATALOG as CATALOG_SETUP # noqa


class BikaSetupCatalog(BaseCatalog):
    implements(IBikaSetupCatalog)


InitializeClass(BikaSetupCatalog)
