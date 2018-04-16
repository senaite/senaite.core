# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import logger
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
    """ Indexes values of desired fields for searches in listing view. All the
    field names added to 'plain_text_fields' will be available to search by
    wildcards.
    Please choose the searchable fields carefully and add only fields that
    can be useful to search by. For example, there is no need to add 'SampleId'
    since 'getId' of AR already contains that value. Nor 'ClientTitle' because
    AR's are/can be filtered by client in Clients' 'AR Listing View'
    :return: values of the fields defined as a string
    """
    entries = []
    plain_text_fields = ('getId', 'getContactFullName', 'getSampleTypeTitle',
                         'getSamplePointTitle',)

    # Concatenate plain text fields as they are
    for field_name in plain_text_fields:
        try:
            value = api.safe_getattr(instance, field_name)
        except:
            logger.error("{} has no attribute called '{}' ".format(
                            repr(instance), field_name))
            continue
        entries.append(value)

    # Concatenate all strings to one text blob
    return " ".join(entries)
