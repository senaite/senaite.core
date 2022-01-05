# -*- coding: utf-8 -*-
#
# XXX: REMOVE AFTER 2.1.0

from App.class_init import InitializeClass
from Products.CMFPlone.CatalogTool import CatalogTool


class BaseCatalog(CatalogTool):
    pass


InitializeClass(BaseCatalog)
