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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from App.class_init import InitializeClass
from bika.lims.catalog.base import BaseCatalog
from bika.lims.interfaces import IBikaSetupCatalog
from zope.interface import implements

SETUP_CATALOG = "bika_setup_catalog"


class BikaSetupCatalog(BaseCatalog):
    """ Catalog for all bika_setup objects
    """
    implements(IBikaSetupCatalog)

    def __init__(self):
        BaseCatalog.__init__(self, SETUP_CATALOG,
                             "Setup Catalog",
                             "BikaSetupCatalog")


InitializeClass(BikaSetupCatalog)
