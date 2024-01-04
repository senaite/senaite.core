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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from App.class_init import InitializeClass
from senaite.core.catalog.base_catalog import COLUMNS as BASE_COLUMNS
from senaite.core.catalog.base_catalog import INDEXES as BASE_INDEXES
from senaite.core.catalog.base_catalog import BaseCatalog
from senaite.core.interfaces import IHaveLabels
from senaite.core.interfaces import ILabelCatalog
from zope.interface import implementer

CATALOG_ID = "senaite_catalog_label"
CATALOG_TITLE = "Senaite Label Catalog"

INDEXES = BASE_INDEXES + [
    # id, indexed attribute, type
    ("labels", "", "KeywordIndex"),
    ("listing_searchable_text", "", "ZCTextIndex"),
]

COLUMNS = BASE_COLUMNS + [
    "getLabels",
]

TYPES = []


@implementer(ILabelCatalog)
class LabelCatalog(BaseCatalog):
    """Catalog for labeled objects
    """
    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_ID, title=CATALOG_TITLE)

    def is_obj_indexable(self, obj, portal_type, mapped_types):
        return IHaveLabels.providedBy(obj)


InitializeClass(LabelCatalog)
