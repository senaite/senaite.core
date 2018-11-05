# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims.subscribers import doActionFor
from bika.lims.utils import changeWorkflowState


def ObjectInitializedEventHandler(instance, event):
    # TODO Workflow Revisit when an Analysis is added to an AR
    wf_tool = getToolByName(instance, 'portal_workflow')

    ar = instance.getRequest()
    ar_state = wf_tool.getInfoFor(ar, 'review_state')

    # Set the state of the analysis depending on the state of the AR.
    if ar_state in ('sample_registered',
                    'to_be_sampled',
                    'sampled',
                    'to_be_preserved',
                    'sample_due',
                    'sample_received'):
        changeWorkflowState(instance, "bika_analysis_workflow", ar_state)
    elif ar_state in ('to_be_verified'):
        # Apply to AR only; we don't want this transition to cascade.
        changeWorkflowState(ar, "bika_ar_workflow", "sample_received")

    return


def ObjectRemovedEventHandler(instance, event):
    """Actions to be done when an analysis is removed from an Analysis Request
    """
    # If all the remaining analyses have been submitted (or verified), try to
    # promote the transition to the Analysis Request
    # Note there is no need to check if the Analysis Request allows a given
    # transition, cause this is already managed by doActionFor
    analysis_request = instance.getRequest()
    doActionFor(analysis_request, "submit")
    doActionFor(analysis_request, "verify")
    return
