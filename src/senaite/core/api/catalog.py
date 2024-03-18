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

import re

import six
from six.moves.urllib.parse import unquote_plus

from bika.lims.api import APIError
from bika.lims.api import get_request
from bika.lims.api import get_tool
from bika.lims.api import safe_unicode
from Products.CMFPlone.UnicodeSplitter import CaseNormalizer
from Products.CMFPlone.UnicodeSplitter import Splitter
from Products.ZCatalog.interfaces import IZCatalog
from Products.ZCTextIndex.ZCTextIndex import PLexicon


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
        return add_zc_text_index(catalog, index, indexed_attrs=indexed_attrs)
    catalog.addIndex(index, index_type)
    # set indexed attribute
    index_obj = get_index(catalog, index)
    if indexed_attrs and hasattr(index_obj, "indexed_attrs"):
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


def add_zc_text_index(catalog, index, lex_id="Lexicon", indexed_attrs=None):
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
        pipeline = [splitter, casenormalizer]
        lexicon = PLexicon(lex_id, "Lexicon", *pipeline)
        catalog._setObject(lex_id, lexicon)

    class extra(object):
        doc_attr = indexed_attrs if indexed_attrs else index
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

    catalog.manage_reindexIndex(index, REQUEST=get_request())
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


def to_searchable_text_qs(qs, op="AND", wildcard=True):
    """Convert the query string for a searchable text index

    https://zope.readthedocs.io/en/latest/zopebook/SearchingZCatalog.html#searching-zctextindexes

    NOTE: we do not support parenthesis, questionmarks or negated searches,
          because this raises quickly parse errors for ZCTextIndexes

    :param qs: search string
    :param op: operator for token concatenation
    :param wildcard: append `*` to the tokens
    :returns: sarchable text string
    """
    OPERATORS = ["AND", "OR"]
    WILDCARDS = ["*", "?"]

    if op not in OPERATORS:
        op = "AND"
    if not isinstance(qs, six.string_types):
        return ""

    def is_op(token):
        return token.upper() in OPERATORS

    def is_wc(char):
        return char in WILDCARDS

    def append_op_after(index, token, tokens):
        # do not append an operator after the last token
        if index == len(tokens) - 1:
            return False
        # do not append an operator if the next token is an operator
        next_token = tokens[num + 1]
        if is_op(next_token):
            return False
        # append an operator (AND/OR) after this token
        return True

    # convert to unicode
    term = unquote_plus(safe_unicode(qs))

    # Wildcards at the beginning are not allowed and therefore removed!
    first_char = term[0] if len(term) > 0 else ""
    if is_wc(first_char):
        term = term.replace(first_char, "", 1)

    # splits the string on all characters that do not match the regex
    regex = r"[^\w\-\_\.\<\>\+\{\}\:\/\?\$]"

    # allow only words when searching just a single character
    if len(term) == 1:
        regex = r"[^\w]"

    tokens = re.split(regex, term, flags=re.U | re.I)

    # filter out all empty tokens
    tokens = filter(None, tokens)

    # cleanup starting operators
    while tokens and is_op(tokens[0]):
        tokens.pop(0)

    # cleanup any trailing operators
    while tokens and is_op(tokens[-1]):
        tokens.pop(-1)

    parts = []

    for num, token in enumerate(tokens):

        # retain wildcards at the end of a token
        last_token_char = token[-1] if len(token) > 0 else ""

        # append operators without changes and continue
        if is_op(token):
            parts.append(token.upper())
            continue

        # append wildcard to token
        if wildcard and not is_op(token) and not is_wc(last_token_char):
            token = token + "*"

        # append the token
        parts.append(token)

        # check if we need to append an operator after the current token
        if append_op_after(num, token, tokens):
            parts.append(op)

    # return the final querystring
    return u" ".join(parts)
