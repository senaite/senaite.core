# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from App.class_init import InitializeClass
from bika.lims.catalog.bika_catalog_tool import BikaCatalogTool
from bika.lims.interfaces import IBikaSetupCatalog


class BikaSetupCatalog(BikaCatalogTool):
    """
    Catalog for all bika_setup objects
    """
    implements(IBikaSetupCatalog)

    def __init__(self):
        BikaCatalogTool.__init__(self, 'bika_setup_catalog',
                                 'Bika Setup Catalog',
                                 'BikaSetupCatalog')

InitializeClass(BikaSetupCatalog)
