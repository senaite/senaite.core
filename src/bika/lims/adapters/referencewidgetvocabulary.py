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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IReferenceWidgetVocabulary
from bika.lims.utils import get_client
from zope.interface import implements

ALLOWED_QUERY_KEYS = [
    "sort_on",
    "sort_order",
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
        query = {}
        for key, value in self.request.form.items():
            if key in ALLOWED_QUERY_KEYS:
                query[key] = value
            elif key in catalog.indexes():
                query[key] = value
            # elif key == "sort_limit":
            #     query[key] = int(value)
            else:
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
        query = self.query
        if not query:
            return []

        # Do the search
        logger.info("Reference Widget Raw Query for catalog {}: {}"
                    .format(self.catalog_name, repr(query)))
        brains = api.search(query, self.catalog_name)
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
        if api.is_string(portal_types):
            portal_types = [portal_types]
        return portal_types
