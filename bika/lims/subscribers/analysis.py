# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.subscribers import doActionFor
from bika.lims.utils import changeWorkflowState
from bika.lims import workflow as wf

# TODO Workflow - Analysis. Move to after_register workflow event?
def ObjectInitializedEventHandler(analysis, event):
    """Actions to be done when an analysis is added in an Analysis Request
    If the analysis request is in state after submission (eg: to_be_verified,
    verified, etc.), forces its transition to "sample_received"
    """
    analysis_request = analysis.getRequest()
    if wf.wasTransitionPerformed(analysis_request, "submit"):
        # Move the AR to 'sample_received' state
        # TODO Workflow - AR - Do a rollback_to_receive transition or such
        changeWorkflowState(analysis_request, "bika_ar_workflow",
                            "sample_received")

    # Reindex the indexes for UIDReference fields on creation!
    analysis.reindexObject(idxs=["getServiceUID"])
    return


def ObjectRemovedEventHandler(analysis, event):
    """Actions to be done when an analysis is removed from an Analysis Request
    """
    # If all the remaining analyses have been submitted (or verified), try to
    # promote the transition to the Analysis Request
    # Note there is no need to check if the Analysis Request allows a given
    # transition, cause this is already managed by doActionFor
    analysis_request = analysis.getRequest()
    doActionFor(analysis_request, "submit")
    doActionFor(analysis_request, "verify")
    return
