# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

## Script (Python) "guard_attach_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

workflow = context.portal_workflow

# Can't do anything to the object if it's cancelled
# reference and duplicate analyses don't have cancellation_state
#if context.portal_type == "Analysis":
if workflow.getInfoFor(context, 'cancellation_state', 'active') == "cancelled":
    return False

if context.portal_type == "AnalysisRequest":
    # Allow transition to 'to_be_verified'
    # if all analyses are at least to_be_verified
    for a in context.getAnalyses(full_objects=True):
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state in ('unassigned', 'assigned', 'attachment_due'):
            return False

if context.portal_type == "Worksheet":
    # Allow transition to 'to_be_verified'
    # if all analyses are at least to_be_verified
    for a in context.getAnalyses():
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state in ('unassigned', 'assigned', 'attachment_due'):
            # Note: referenceanalyses and duplicateanalysis can
            # still have review_state = "assigned".
            return False

return True
