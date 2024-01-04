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

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IReferenceWidgetVocabulary
from bika.lims.utils import get_client
from Products.ZCTextIndex.ParseTree import ParseError
from zope.interface import implements

ALLOWED_QUERY_KEYS = [
    "sort_on",
    "sort_order",
]

# Search index placeholder for dynamic lookup by the search endpoint
SEARCH_INDEX_MARKER = "__search__"

# default search index name
DEFAULT_SEARCH_INDEXES = [
    "listing_searchable_text",
    "Title",
]


class DefaultReferenceWidgetVocabulary(object):
    implements(IReferenceWidgetVocabulary)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def catalog_name(self):
        """Returns the catalog name to be used for the search
        """
        return self.request.get("catalog")

    @property
    def query(self):
        """Build the raw request from the query params
        """
        catalog = api.get_tool(self.catalog_name)
        indexes = catalog.indexes()
        raw_query = dict(self.request.form.items())

        query = {}
        for key, value in raw_query.items():
            if key in ALLOWED_QUERY_KEYS:
                query[key] = value
            elif key in indexes:
                query[key] = value
            elif key == SEARCH_INDEX_MARKER:
                # find a suitable ZCText index for the search
                can_search = False
                search_indexes = DEFAULT_SEARCH_INDEXES[:]
                # check if we have a content specific search index
                portal_type = raw_query.get("portal_type")
                if api.is_string(portal_type):
                    index = "{}_searchable_text".format(portal_type.lower())
                    search_indexes.insert(0, index)
                # check if one of the search indexes match
                for index in search_indexes:
                    if index in indexes:
                        query[index] = value
                        can_search = True
                        break
                if not can_search:
                    logger.warn("No text index found for query '%s'!" % value)
            else:
                # skip unknown indexes for the query
                continue
        return query

    def get_raw_query(self):
        """BBB
        """
        return self.query

    def __call__(self):
        # Get the raw query to use
        # Raw query is built from base query baseline, including additional
        # parameters defined in the request and the search query as well
        raw_query = self.get_raw_query()
        if not raw_query:
            return []

        # JSON parse all query values
        # NOTE: The raw query might have JSON encoded values,
        #       e.g. it could contain {"is_active": "true"}
        query = {}
        for key, value in raw_query.items():
            query[key] = api.parse_json(value, value)

        # Do the search
        logger.info("Reference Widget Raw Query for catalog {}: {}"
                    .format(self.catalog_name, repr(query)))
        try:
            brains = api.search(query, self.catalog_name)
        except ParseError:
            brains = []
        logger.info("Found {} results".format(len(brains)))
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
        if api.is_string(portal_types):
            portal_types = [portal_types]
        return portal_types
