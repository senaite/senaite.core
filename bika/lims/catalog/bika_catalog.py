# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements
from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.interfaces import IBikaCatalog


class BikaCatalog(BikaCatalogTool):
    """
    Catalog for Bika Catalog
    """
    implements(IBikaCatalog)

    def __init__(self):
        BikaCatalogTool.__init__(self, 'bika_catalog',
                                 'Bika Catalog',
                                 'BikaCatalog')

InitializeClass(BikaCatalog)
