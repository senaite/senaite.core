# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.workflow import doActionFor as do_action_for

AR_WORKFLOW_ID = "bika_ar_workflow"


def do_action_to_ancestors(analysis_request, transition_id):
    """Promotes the transitiion passed in to ancestors, if any
    """
    parent_ar = analysis_request.getParentAnalysisRequest()
    if parent_ar:
        do_action_for(parent_ar, transition_id)


def do_action_to_descendants(analysis_request, transition_id):
    """Cascades the transition passed in to the descendant partitions
    """
    for partition in analysis_request.getDescendants(all_descendants=False):
        do_action_for(partition, transition_id)


def do_action_to_analyses(analysis_request, transition_id, all_analyses=False):
    """Cascades the transition to the analysis request analyses. If all_analyses
    is set to True, the transition will be triggered for all analyses of this
    analysis request, those from the descendant partitions included.
    """
    analyses = list()
    if all_analyses:
        analyses = analysis_request.getAnalyses(full_objects=True)
    else:
        analyses = analysis_request.objectValues("Analysis")
    for analysis in analyses:
        do_action_for(analysis, transition_id)
