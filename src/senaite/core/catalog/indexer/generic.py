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
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.CatalogTool import \
    sortable_title as plone_sortable_title
from Products.CMFPlone.utils import safe_callable
from senaite.core.catalog import SENAITE_CATALOG
from senaite.core.catalog.utils import get_searchable_text_tokens
from senaite.core.interfaces import ISenaiteCatalog


@indexer(IContentish)
def is_active(instance):
    """Returns False if the status of the instance is 'cancelled' or 'inactive'.
    Otherwise returns True
    """
    return api.is_active(instance)


@indexer(IContentish)
def title(instance):
    """Populate the `title` FieldIndex with the unicode Title().

    The `title` FieldIndex defined in base_catalog has no `attr` set,
    so the catalog wrapper reads `obj.title` and delegates here for
    every IContentish object. Returning `api.safe_unicode(Title())`
    gives the index a single, consistent unicode key type across all
    content types so non-ASCII titles can be queried as unicode:

        catalog(title=u"Café")

    The `Title` metadata column is independent of this indexer and
    keeps whatever the content's `Title()` method returns (bytes for
    most SENAITE AT types, unicode for DX content), so existing
    consumers of `brain.Title` are unaffected.
    """
    return api.safe_unicode(instance.Title())


@indexer(IContentish)
def sortable_title(instance):
    """Uses the default Plone sortable_text index lower-case
    """
    title = plone_sortable_title(instance)
    if safe_callable(title):
        title = title()
    return title.lower()


@indexer(IContentish, ISenaiteCatalog)
def listing_searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    tokens = get_searchable_text_tokens(instance, SENAITE_CATALOG)
    return u" ".join(tokens)
