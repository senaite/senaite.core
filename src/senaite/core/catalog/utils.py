# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IListingSearchableTextProvider
from Products.CMFPlone.CatalogTool import \
    sortable_title as plone_sortable_title
from Products.CMFPlone.utils import safe_callable
from zope.component import getAdapters


def get_searchable_text_tokens(instance, catalog_name,
                               exclude_field_names=None,
                               include_field_names=None):
    """Retrieves all the values of metadata columns in the catalog for
    wildcard searches

    :param instance: the object to retrieve metadata/values from
    :param catalog_name: the catalog to retrieve metadata from
    :param exclude_field_names: field names to exclude from the metadata
    :param include_field_names: field names to include, even if no metadata
    :returns: list of unified searchable text tokes
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

    # Extend metadata entries with pluggable text providers
    for name, adapter in getAdapters((instance, catalog),
                                     IListingSearchableTextProvider):
        value = adapter()
        if isinstance(value, (list, tuple)):
            values = map(api.to_searchable_text_metadata, value)
            entries.update(values)
        else:
            value = api.to_searchable_text_metadata(value)
            entries.add(value)

    # Remove empties
    entries = filter(None, entries)

    # return a list of searchable text tokes
    return list(entries)


def get_metadata_for(instance, catalog):
    """Returns the metadata for the given instance from the specified catalog
    """
    path = api.get_path(instance)
    try:
        return catalog.getMetadataForUID(path)
    except KeyError:
        logger.info("Generating catalog metadata for '{}' manually"
                    .format(path))
        metadata = {}
        for key in catalog.schema():
            attr = getattr(instance, key, None)
            if callable(attr):
                attr = attr()
            metadata[key] = attr
        return metadata


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
