# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.workflow import getCurrentState
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
    """

    :param instance:
    :return:
    """
    entries = []
    plain_text_fields = ("getId", "getSampleID")

    # Concatenate plain text fields as they are
    for field_name in plain_text_fields:
        value = api.safe_getattr(instance, field_name)
        entries.append(value)

    # Concatenate all strings to one text blob
    return " ".join(entries)
