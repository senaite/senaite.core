# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

## Script (Python) "guard_submit_transition"
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
if workflow.getInfoFor(context, 'cancellation_state', 'active') == "cancelled":
    return False

if context.portal_type == "AnalysisRequest":
    # Only transition to 'attachment_due' if all analyses are at least there.
    has_analyses = False
    for a in context.getAnalyses(full_objects=True):
        has_analyses = True
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state == "registered":
            return False
    return has_analyses

if context.portal_type == "Worksheet":

    # Only transition to 'attachment_due' if all analyses are at least there.
    has_analyses = False
    workflow = context.portal_workflow
    for a in context.getAnalyses():
        has_analyses = True
        review_state = workflow.getInfoFor(a, 'review_state', '')
        if review_state in ('registered', 'assigned',):
            # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
            return False
    return has_analyses
