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

from plone.indexer import indexer

from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.indexers import get_metadata_for
from bika.lims.interfaces import IAnalysisRequest, \
    IBikaCatalogAnalysisRequestListing


@indexer(IAnalysisRequest)
def assigned_state(instance):
    """Returns `assigned` or `unassigned` depending on the state of the
    analyses the analysisrequest contains. Return `unassigned` if the Analysis
    Request has at least one analysis in `unassigned` state.
    Otherwise, returns `assigned`
    """
    analyses = instance.getAnalyses()
    if not analyses:
        return "unassigned"
    for analysis in analyses:
        analysis_object = api.get_object(analysis)
        if not analysis_object.getWorksheet():
            return "unassigned"
    return "assigned"


@indexer(IAnalysisRequest, IBikaCatalogAnalysisRequestListing)
def listing_searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    entries = set()
    catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    metadata = get_metadata_for(instance, catalog)
    for key, brain_value in metadata.items():
        instance_value = api.safe_getattr(instance, key, None)
        parsed = api.to_searchable_text_metadata(brain_value or instance_value)
        entries.add(parsed)

    # add metadata of all descendants
    for descendant in instance.getDescendants():
        entries.add(listing_searchable_text(descendant)())

    # Concatenate all strings to one text blob
    return " ".join(entries)


@indexer(IAnalysisRequest)
def is_received(instance):
    """Returns whether the Analysis Request has been received
    """
    if instance.getDateReceived():
        return True
    return False
