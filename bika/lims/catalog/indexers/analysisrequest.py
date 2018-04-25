# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer


@indexer(IAnalysisRequest)
def assigned_state(instance):
    """Returns `assigned` or `unassigned` depending on the state of the
    analyses the analysisrequest contains. Return `unassigned` if the Analysis
    Request does not contain any analysis or if has at least one in `unassigned`
    state. Otherwise, returns `assigned`"""
    analyses = instance.getAnalyses()
    if not analyses:
        return 'unassigned'

    state_var = 'worksheetanalysis_review_state'
    for analysis in analyses:
        state = api.get_workflow_status_of(analysis, state_var)
        if state != 'assigned':
            return 'unassigned'

    return 'assigned'


@indexer(IAnalysisRequest)
def listing_searchable_text(instance):
    """ Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    entries = set()
    catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    columns = catalog.schema()

    for column in columns:
        value = api.safe_getattr(instance, column, None)
        parsed = api.to_searchable_text_metadata(value)
        if parsed:
            entries.add(parsed)

    # Concatenate all strings to one text blob
    return " ".join(entries)
