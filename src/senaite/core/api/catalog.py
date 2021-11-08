# -*- coding: utf-8 -*-

import six

from bika.lims.api import get_tool
from Products.ZCatalog.interfaces import IZCatalog
from Products.ZCTextIndex.Lexicon import StopWordAndSingleCharRemover
from Products.CMFPlone.UnicodeSplitter import CaseNormalizer
from Products.CMFPlone.UnicodeSplitter import Splitter
from Products.ZCTextIndex.ZCTextIndex import PLexicon
from Products.ZCatalog.ZCatalog import ZCatalog
from bika.lims.api import APIError


def get_catalog(name_or_obj):
    """Get the catalog by name or from the object

    :param name_or_obj: name of the catalog or a catalog object
    :returns: catalog object
    """
    if is_catalog(name_or_obj):
        return name_or_obj

    catalog = None
    if isinstance(name_or_obj, six.string_types):
        catalog = get_tool(name_or_obj)
    if not is_catalog(catalog):
        raise APIError("No catalog found for %s" % repr(name_or_obj))
    return catalog


def is_catalog(obj):
    """Checks if the given object is a catalog

    :param obj: An object
    :returns: True/False if the object is a ZCatalog object
    """
    return IZCatalog.providedBy(obj)


def get_indexes(catalog):
    """Return the indexes of the catalog

    :param catalog: Catalog object
    :returns: List of all index names
    """
    catalog = get_catalog(catalog)
    return catalog.indexes()


def get_columns(catalog):
    """Return the columns of the catalog

    :param catalog: Catalog object
    :returns: List of all column names
    """
    catalog = get_catalog(catalog)
    return catalog.schema()


def add_index(catalog, index, index_type, indexed_attrs=None):
    """Add an index to the catalog

    :param catalog: Catalog object
    :param index: Index id
    :returns: True when the index was added successfully otherwise False
    """
    catalog = get_catalog(catalog)
    indexes = get_indexes(catalog)
    if index in indexes:
        return False
    if index_type == "ZCTextIndex":
        return add_zc_text_index(catalog, index)
    catalog.addIndex(index, index_type)
    # set indexed attribute
    if indexed_attrs and hasattr(index, "indexed_attrs"):
        index_obj = get_index(index)
        if not isinstance(indexed_attrs, list):
            indexed_attrs = [indexed_attrs]
        index_obj.indexed_attrs = indexed_attrs
    return True


def del_index(catalog, index):
    """Delete an index from the catalog

    :param catalog: Catalog object
    :param index: Index id
    :returns: True when the index was deleted successfully otherwise False
    """
    catalog = get_catalog(catalog)
    indexes = get_indexes(catalog)
    if index not in indexes:
        return False
    catalog.delIndex(index)
    return True


def get_index(catalog, index):
    """Get an index from the catalog

    :param catalog: Catalog object
    :param index: Index id
    :returns: Index object or None
    """
    catalog = get_catalog(catalog)
    indexes = get_indexes(catalog)
    if index not in indexes:
        return None
    return catalog.Indexes[index]


def add_zc_text_index(catalog, index, lex_id="Lexicon"):
    """Add ZC text index to the catalog

    :param catalog: Catalog object
    :param index: Index id
    :returns: True when the index was added successfully, otherwise False
    """
    catalog = get_catalog(catalog)
    indexes = get_indexes(catalog)

    if index in indexes:
        return False

    # check if the lexicon exists
    lexicon = getattr(catalog, lex_id, None)
    if lexicon is None:
        # create the lexicon first
        splitter = Splitter()
        casenormalizer = CaseNormalizer()
        stopwordremover = StopWordAndSingleCharRemover()
        pipeline = [splitter, casenormalizer, stopwordremover]
        lexicon = PLexicon(lex_id, "Lexicon", *pipeline)
        catalog._setObject(lex_id, lexicon)

    class extra(object):
        doc_attr = index
        lexicon_id = lex_id
        index_type = "Okapi BM25 Rank"

    catalog.addIndex(index, "ZCTextIndex", extra)
    return True


def reindex_index(catalog, index):
    """Reindex the index of the catalog

    :param catalog: Catalog object
    :param index: Index id
    :returns: True when the index was reindexd successfully, otherwise False
    """
    catalog = get_catalog(catalog)
    indexes = get_indexes(catalog)

    if index not in indexes:
        return False

    catalog.manage_reindexIndex(index)
    return True


def add_column(catalog, column):
    """Add a column to the catalog

    :param catalog: Catalog object
    :param column: Column name
    :returns: True when the column  was added successfully, otherwise False
    """
    catalog = get_catalog(catalog)
    columns = get_columns(catalog)

    if column in columns:
        return False

    catalog.addColumn(column)
    return True


def del_column(catalog, column):
    """Delete a column from the catalog

    :param catalog: Catalog object
    :param column: Column name
    :returns: True when the column  was deleted successfully, otherwise False
    """
    catalog = get_catalog(catalog)
    columns = get_columns(catalog)

    if column not in columns:
        return False

    catalog.delColumn(column)
    return True
