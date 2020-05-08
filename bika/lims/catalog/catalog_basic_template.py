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

BASE_CATALOG_INDEXES = {
    # Returns the catalog id
    "id": "FieldIndex",
    "title": "FieldIndex",
    # Return the object id
    "getId": "FieldIndex",
    "portal_type": "FieldIndex",
    "object_provides": "KeywordIndex",
    "UID": "UUIDIndex",
    # created returns a DataTime object
    "created": "DateIndex",
    # created returns a string object with date format
    "CreationDate": "DateIndex",
    "Creator": "FieldIndex",
    # allowedRolesAndUsers is compulsory if we are going to run
    # advancedqueries in this catalog.
    "allowedRolesAndUsers": "KeywordIndex",
    "review_state": "FieldIndex",
    # Necessary to avoid reindexing whole catalog when we need to
    # reindex only one object. ExtendedPathIndex also could be used.
    "path": "PathIndex",
    "is_active": "BooleanIndex",
}

BASE_CATALOG_COLUMNS = [
    "UID",
    "getId",
    "meta_type",
    "Title",
    "review_state",
    "state_title",
    "portal_type",
    # allowedRolesAndUsers is compulsory if we are going to run
    # advancedqueries in this catalog.
    "allowedRolesAndUsers",
    "created",
    "Creator",
]
