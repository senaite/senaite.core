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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IOrganisation
from plone.indexer import indexer


@indexer(IOrganisation)
def title(instance):
    """Organisation objects does not use the built-in title, rather it uses
    Name schema field. We need this type-specific index to simulate the default
    behavior for index `title`.

    The `Name` is coerced to unicode (like the generic `title` indexer) so the
    shared `title` FieldIndex holds a single, consistent unicode key type. A
    non-ASCII byte-string key would otherwise raise a `UnicodeDecodeError` on
    Python 2 when compared against a unicode query value.
    """
    name = getattr(instance, "Name", None)
    if not name:
        return u""
    return api.safe_unicode(name)
