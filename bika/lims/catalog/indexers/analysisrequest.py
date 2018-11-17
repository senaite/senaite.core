# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from plone.indexer import indexer

from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.interfaces import IAnalysisRequest


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


@indexer(IAnalysisRequest)
def listing_searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    entries = set()
    catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    columns = catalog.schema()
    brains = catalog({"UID": api.get_uid(instance)})
    brain = brains[0] if brains else None
    for column in columns:
        brain_value = api.safe_getattr(brain, column, None)
        instance_value = api.safe_getattr(instance, column, None)
        parsed = api.to_searchable_text_metadata(brain_value or instance_value)
        entries.add(parsed)

    # add metadata of all descendants
    for descendant in instance.getDescendants():
        entries.add(listing_searchable_text(descendant)())

    # Concatenate all strings to one text blob
    return " ".join(entries)
