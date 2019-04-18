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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from Products.AdvancedQuery import Or, MatchRegexp, Generic
from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IReferenceWidgetVocabulary
from bika.lims.utils import to_unicode as _u
from bika.lims.utils import to_utf8 as _c
from zope.interface import implements


class DefaultReferenceWidgetVocabulary(object):
    implements(IReferenceWidgetVocabulary)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def search_fields(self):
        """Returns the object field names to search against
        """
        search_fields = self.request.get("search_fields", "[]")
        search_fields = json.loads(_u(search_fields))
        if not search_fields:
            return ("Title",)
        return search_fields

    @property
    def search_term(self):
        """Returns the search term
        """
        search_term = _c(self.request.get("searchTerm", ""))
        return search_term.lower().strip()

    @property
    def force_all(self):
        """Returns whether all records must be displayed if no match is found
        """
        force_all = self.request.get("force_all", "").lower()
        return force_all in ["1", "true"] or False

    @property
    def catalog_name(self):
        """Returns the catalog name to be used for the search
        """
        catalog_name = self.request.get("catalog_name", None)
        return catalog_name or "portal_catalog"

    @property
    def base_query(self):
        """Returns the base query to use. This is, the query with the basic
        filtering criteria to be used as the baseline. Search criterias defined
        in base_query are restricive (AND statments, not included in OR-like)
        """
        return self.get_query_from_request("base_query")

    @property
    def search_query(self):
        """Returns the search query.
        """
        return self.get_query_from_request("search_query")

    def get_query_from_request(self, name):
        """Returns the query inferred from the request
        """
        query = self.request.get(name, "{}")
        # json.loads does unicode conversion, which will fail in the catalog
        # search for some cases. So we need to convert the strings to utf8
        # https://github.com/senaite/senaite.core/issues/443
        query = json.loads(query)
        query = self.to_utf8(query)

        # Add sorting criterias
        sorting = self.resolve_sorting(query)
        query.update(sorting)
        return query

    def get_raw_query(self):
        """Returns the raw query to use for current search, based on the
        base query + update query
        """
        query = self.base_query.copy()
        search_query = self.search_query.copy()
        query.update(search_query)

        # Check if sort_on is an index and if is sortable. Otherwise, assume
        # the sorting must be done manually
        catalog = api.get_tool(self.catalog_name)
        sort_on = query.get("sort_on", None)
        if sort_on and not self.is_sortable_index(sort_on, catalog):
            del(query["sort_on"])
        return query

    def resolve_sorting(self, query):
        """Resolves the sorting criteria for the given query based on the
        configuration parameters from the request
        """
        sorting = {}

        # Sort on
        sort_on = self.request.get("sidx", None)
        sort_on = sort_on or self.request.get("sort_on", None)
        sort_on = sort_on or query.get("sidx", None)
        sort_on = sort_on or query.get("sort_on", None)
        sort_on = sort_on == "Title" and "sortable_title" or sort_on
        if sort_on:
            sorting["sort_on"] = sort_on

            # Sort order
            sort_order = self.request.get("sord", None)
            sort_order = sort_order or self.request.get("sort_order", None)
            sort_order = sort_order or query.get("sord", None)
            sort_order = sort_order or query.get("sort_order", None)
            if (sort_order in ["desc", "reverse", "rev", "descending"]):
                sorting["sort_order"] = "descending"
            else:
                sorting["sort_order"] = "ascending"

            # Sort limit
            sort_limit = api.to_int(query.get("limit", 0), default=0)
            sort_limit = sort_limit or api.to_int(
                self.request.get("sort_limit", 0),
                default=0)
            if sort_limit:
                sorting["sort_limit"] = sort_limit

        return sorting

    def is_sortable_index(self, index_name, catalog):
        """Returns whether the index is sortable
        """
        if not index_name:
            return False
        index = catalog.Indexes.get(index_name, None)
        if not index:
            return False
        return index.meta_type in ["FieldIndex", "DateIndex"]

    def get_index(self, field_name, catalog):
        """Returns the index of the catalog for the given field_name, if any
        """
        index = catalog.Indexes.get(field_name, None)
        if index:
            if index.meta_type == "DateIndex":
                # For some reason, we do not handle DateIndex
                logger.warn("Unhandled DateIndex search on '%s'" % field_name)
                return None
            return index

        elif field_name == "Title":
            # Legacy
            return self.get_index("sortable_title", catalog)

        return None

    def try_advanced_query(self, query, search_term, search_fields, catalog):
        """Returns an advanced query object if suitable for the query passed in
        """
        if not search_term:
            return None

        criteria = []
        for field in search_fields:
            index = self.get_index(field, catalog)
            if not index:
                continue

            if index.meta_type == "TextIndexNG3":
                # We can handle this search without AdvancedQuery, no need
                # to go further
                return None

            elif index.meta_type == "ZCTextIndex":
                # We need to add the * at the end to allow LIKE-searches
                term = "{}*".format(search_term)
                criteria.append(MatchRegexp(field, term))

            elif index.meta_type == "FieldIndex":
                criteria.append(MatchRegexp(field, search_term))

            else:
                criteria.append(Generic(field, search_term))

        if criteria:
            # Advanced search
            advanced_query = catalog.makeAdvancedQuery(query)
            aq_or = Or()
            for criteria in criteria:
                aq_or.addSubquery(criteria)
            advanced_query &= aq_or
            return advanced_query

        # No need of advanced query
        return None

    def search(self, query, search_term, search_fields, catalog):
        """Performs a search against the catalog and returns the brains
        """
        # Try with an advanced query
        advanced_query = self.try_advanced_query(query, search_term,
                                                 search_fields, catalog)
        if advanced_query:
            logger.info("Reference Widget Query: {}".format(repr(query)))
            logger.warn("Advanced query required. Consider to use TextIndexNG3")
            brains = catalog.evalAdvancedQuery(advanced_query)

            # We need to apply the limit manually here
            sort_limit = int(query.get("sort_limit", 0))
            if sort_limit > 0 and len(brains) > sort_limit:
                return brains[:sort_limit]
            return brains

        # Create a classic query
        if search_term:
            for field_name in search_fields:
                index = self.get_index(field_name, catalog)
                if index.meta_type == "TextIndexNG3":
                    query[index.id] = "{}*".format(search_term)
                else:
                    logger.warn("Index '{}' not found in '{}'"
                                .format(field_name, catalog.id))

        logger.info("Reference Widget Query: {}".format(repr(query)))
        return catalog(query)

    def __call__(self, result=None, specification=None, **kwargs):

        catalog = api.get_tool(self.catalog_name)

        # Get the raw query to use
        # Raw query is built from base query baseline, including additional
        # parameters defined in the request and the search query as well
        query = self.get_raw_query()
        if not query:
            return []

        # Do the search
        logger.info("Reference Widget Raw Query: {}".format(repr(query)))
        brains = self.search(query, self.search_term, self.search_fields, catalog)

        # If no matches, then just base_query alone ("show all if no match")
        if not brains and self.force_all:
            query = self.base_query.copy()
            logger.info("No objects!. Get them'all: {}".format(repr(query)))
            brains = catalog(query)

        logger.info("Returned objects: {}".format(len(brains)))
        return brains

    def to_utf8(self, data):
        """
        Convert unicode values to strings even if they belong to lists or dicts.
        :param data: an object.
        :return: The object with all unicode values converted to string.
        """
        # if this is a unicode string, return its string representation
        if isinstance(data, unicode):
            return data.encode('utf-8')

        # if this is a list of values, return list of string values
        if isinstance(data, list):
            return [self.to_utf8(item) for item in data]

        # if this is a dictionary, return dictionary of string keys and values
        if isinstance(data, dict):
            return {
                self.to_utf8(key): self.to_utf8(value)
                for key, value in data.iteritems()
            }

        # if it's anything else, return it in its original form
        return data
