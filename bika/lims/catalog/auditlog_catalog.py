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
from bika.lims.interfaces import IAuditLogCatalog
from zope.interface import implements


# Using a variable to avoid plain strings in code
CATALOG_AUDITLOG = "auditlog_catalog"

# Defining the indexes for this catalog
_indexes = {
    "title": "FieldIndex",
    "getId": "FieldIndex",
    "portal_type": "FieldIndex",
    "object_provides": "KeywordIndex",
    "UID": "UUIDIndex",
    "review_state": "FieldIndex",
    "is_active": "BooleanIndex",
    "modified": "DateIndex",
    "modifiers": "KeywordIndex",
    "actor": "FieldIndex",
    "action": "FieldIndex",
    "listing_searchable_text": "TextIndexNG3",
    "snapshot_created": "DateIndex",
    "snapshot_version": "FieldIndex",
    "path": "PathIndex",
}
# Defining the columns for this catalog
_columns = []
# Defining the types for this catalog
_types = []

catalog_auditlog_definition = {
    CATALOG_AUDITLOG: {
        "types": _types,
        "indexes": _indexes,
        "columns": _columns,
    }
}


class AuditLogCatalog(BaseCatalog):
    """Audit Log Catalog
    """
    implements(IAuditLogCatalog)

    def __init__(self):
        BaseCatalog.__init__(self, CATALOG_AUDITLOG,
                             "Audit Log Catalog",
                             "AuditLogCatalog")


InitializeClass(AuditLogCatalog)
