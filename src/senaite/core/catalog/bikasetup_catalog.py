# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from zope.interface import implements
from App.class_init import InitializeClass
from senaite.core.catalog.bika_catalog_tool import BikaCatalogTool
from senaite.core.interfaces import IBikaSetupCatalog


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
