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

import json
import six

from zope.interface import implements

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IReferenceWidgetVocabulary
from bika.lims.utils import get_client
from bika.lims.utils import to_unicode as _u
from bika.lims.utils import to_utf8 as _c


class DefaultReferenceWidgetVocabulary(object):
    implements(IReferenceWidgetVocabulary)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def search_fields(self):
        """Returns the object field names to search against
        """
        search_fields = self.request.get("search_fields", None)
        if not search_fields:
            return []

        search_fields = json.loads(_u(search_fields))
        return search_fields

    @property
    def search_field(self):
        """Returns the field name to search for
        """
        search_fields = self.search_fields
        if not search_fields:
            return "Title"
        return search_fields[0]

    @property
    def search_term(self):
        """Returns the search term
        """
        search_term = _c(self.request.get("searchTerm", ""))
        return search_term.lower().strip()

    @property
    def minimum_length(self):
        """Minimum required length of the search term
        """
        min_length = self.request.get("minLength", 0)
        return api.to_int(min_length, 0)

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

    def get_query_from_request(self, name):
        """Returns the query inferred from the request
        """
        query = self.request.get(name, "{}")
        # json.loads does unicode conversion, which will fail in the catalog
        # search for some cases. So we need to convert the strings to utf8
        # https://github.com/senaite/senaite.core/issues/443
        query = json.loads(query)
        return self.to_utf8(query)

    def get_raw_query(self):
        """Returns the raw query to use for current search, based on the
        base query + update query
        """
        query = self.base_query.copy()
        search_query = self.search_query.copy()
        query.update(search_query)

        # Add sorting criteria
        sorting = self.resolve_sorting(query)
        query.update(sorting)

        # Check if sort_on is an index and if is sortable. Otherwise, assume
        # the sorting must be done manually
        catalog = api.get_tool(self.catalog_name)
        sort_on = query.get("sort_on", None)
        if sort_on and not self.is_sortable_index(sort_on, catalog):
            del(query["sort_on"])
        return query

    def resolve_sorting(self, query):
        """Resolves the sorting criteria for the given query
        """
        sorting = {}

        # Sort on
        sort_on = query.get("sidx", None)
        sort_on = sort_on or query.get("sort_on", None)
        sort_on = sort_on == "Title" and "sortable_title" or sort_on
        if sort_on:
            sorting["sort_on"] = sort_on

            # Sort order
            sort_order = query.get("sord", None)
            sort_order = sort_order or query.get("sort_order", None)
            if sort_order in ["desc", "reverse", "rev", "descending"]:
                sorting["sort_order"] = "descending"
            else:
                sorting["sort_order"] = "ascending"

            # Sort limit
            sort_limit = query.get("sort_limit", query.get("limit"))
            sort_limit = api.to_int(sort_limit, default=30)
            if sort_limit:
                sorting["sort_limit"] = sort_limit

        return sorting

    def is_sortable_index(self, index_name, catalog):
        """Returns whether the index is sortable
        """
        index = self.get_index(index_name, catalog)
        if not index:
            return False
        return index.meta_type in ["FieldIndex", "DateIndex"]

    def get_index(self, field_name, catalog):
        """Returns the index of the catalog for the given field_name, if any
        """
        index = catalog.Indexes.get(field_name, None)
        if not index and field_name == "Title":
            # Legacy
            return self.get_index("sortable_title", catalog)
        return index

    def search(self, query, search_term, search_field, catalog):
        """Performs a search against the catalog and returns the brains
        """
        logger.info("Reference Widget Catalog: {}".format(catalog.id))
        if not search_term:
            return catalog(query)

        index = self.get_index(search_field, catalog)
        if not index:
            logger.warn("*** Index not found: '{}'".format(search_field))
            return []

        meta = index.meta_type
        if meta == "TextIndexNG3":
            query[index.id] = "{}*".format(search_term)

        elif meta == "ZCTextIndex":
            logger.warn("*** Field '{}' ({}). Better use TextIndexNG3"
                        .format(meta, search_field))
            query[index.id] = "{}*".format(search_term)

        elif meta in ["FieldIndex", "KeywordIndex"]:
            logger.warn("*** Field '{}' ({}). Better use TextIndexNG3"
                        .format(meta, search_field))
            query[index.id] = search_term

        else:
            logger.warn("*** Index '{}' ({}) not supported"
                        .format(search_field, meta))
            return []

        logger.info("Reference Widget Query: {}".format(repr(query)))
        return catalog(query)

    def __call__(self):
        # If search term, check if its length is above the minLength
        search_term = self.search_term
        if search_term and len(search_term) < self.minimum_length:
            return []

        # Get the raw query to use
        # Raw query is built from base query baseline, including additional
        # parameters defined in the request and the search query as well
        query = self.get_raw_query()
        if not query:
            return []

        # Do the search
        logger.info("Reference Widget Raw Query: {}".format(repr(query)))
        catalog = api.get_tool(self.catalog_name)
        brains = self.search(query, search_term, self.search_field, catalog)

        # If no matches, then just base_query alone ("show all if no match")
        if not brains and self.force_all:
            query = self.base_query.copy()
            sorting = self.resolve_sorting(query)
            query.update(sorting)
            brains = catalog(query)

        logger.info("Returned objects: {}".format(len(brains)))
        return brains


class ClientAwareReferenceWidgetVocabulary(DefaultReferenceWidgetVocabulary):
    """Injects search criteria (filters) in the query when the current context
    is, belongs or is associated to a Client
    """

    # portal_types that might be bound to a client
    client_bound_types = [
        "Contact",
        "Batch",
        "AnalysisProfile",
        "AnalysisSpec",
        "ARTemplate",
        "SamplePoint"
    ]

    def get_raw_query(self):
        """Returns the raw query to use for current search, based on the
        base query + update query
        """
        query = super(
            ClientAwareReferenceWidgetVocabulary, self).get_raw_query()

        if self.is_client_aware(query):

            client = get_client(self.context)
            client_uid = client and api.get_uid(client) or None

            if client_uid:
                # Apply the search criteria for this client
                # Contact is the only object bound to a Client that is stored
                # in portal_catalog. And in this catalog, getClientUID does not
                # exist, rather getParentUID
                if "Contact" in self.get_portal_types(query):
                    query["getParentUID"] = [client_uid]
                else:
                    query["getClientUID"] = [client_uid, ""]

        return query

    def is_client_aware(self, query):
        """Returns whether the query passed in requires a filter by client
        """
        portal_types = self.get_portal_types(query)
        intersect = set(portal_types).intersection(self.client_bound_types)
        return len(intersect) > 0

    def get_portal_types(self, query):
        """Return the list of portal types from the query passed-in
        """
        portal_types = query.get("portal_type", [])
        if isinstance(portal_types, six.string_types):
            portal_types = [portal_types]
        return portal_types
