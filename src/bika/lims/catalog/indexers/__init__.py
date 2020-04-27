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

from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.bika_catalog import BIKA_CATALOG
from bika.lims.interfaces import IBikaCatalog
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.CatalogTool import \
    sortable_title as plone_sortable_title
from Products.CMFPlone.utils import safe_callable


@indexer(IContentish)
def is_active(instance):
    """Returns False if the status of the instance is 'cancelled' or 'inactive'.
    Otherwise returns True
    """
    return api.is_active(instance)


@indexer(IContentish)
def sortable_title(instance):
    """Uses the default Plone sortable_text index lower-case
    """
    title = plone_sortable_title(instance)
    if safe_callable(title):
        title = title()
    return title.lower()


def sortable_sortkey_title(instance):
    """Returns a sortable title as a mxin of sortkey + lowercase sortable_title
    """
    title = sortable_title(instance)
    if safe_callable(title):
        title = title()

    sort_key = instance.getSortKey()
    if sort_key is None:
        sort_key = 999999

    return "{:010.3f}{}".format(sort_key, title)


@indexer(IContentish, IBikaCatalog)
def listing_searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    return generic_listing_searchable_text(instance, BIKA_CATALOG)


def get_metadata_for(instance, catalog):
    """Returns the metadata for the given instance from the specified catalog
    """
    path = api.get_path(instance)
    try:
        return catalog.getMetadataForUID(path)
    except KeyError:
        logger.warn("Cannot get metadata from {}. Path not found: {}"
                    .format(catalog.id, path))
        return {}


def generic_listing_searchable_text(instance, catalog_name,
                                    exclude_field_names=None,
                                    include_field_names=None):
    """Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :param instance: the object to retrieve metadata/values from
    :param catalog_name: the catalog to retrieve metadata from
    :param exclude_field_names: field names to exclude from the metadata
    :param include_field_names: field names to include, even if no metadata
    """
    entries = set()

    # Fields to include/exclude
    include = include_field_names or []
    exclude = exclude_field_names or []

    # Get the metadata fields from this instance and catalog
    catalog = api.get_tool(catalog_name)
    metadata = get_metadata_for(instance, catalog)
    for key, brain_value in metadata.items():
        if key in exclude:
            continue
        elif key in include:
            # A metadata field already
            include.remove(key)

        instance_value = api.safe_getattr(instance, key, None)
        parsed = api.to_searchable_text_metadata(brain_value or instance_value)
        entries.add(parsed)

    # Include values from additional fields
    for field_name in include:
        field_value = api.safe_getattr(instance, field_name, None)
        field_value = api.to_searchable_text_metadata(field_value)
        entries.add(field_value)

    # Remove empties
    entries = filter(None, entries)

    # Concatenate all strings to one text blob
    return " ".join(entries)
