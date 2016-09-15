# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

## Script (Python) "guard_assign_transition"
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
if workflow.getInfoFor(context, 'cancellation_state', '') == "cancelled":
    return False

if context.portal_type != 'AnalysisRequest':
    return True

if not context.getAnalyses(worksheetanalysis_review_state = 'assigned'):
    return False

if context.getAnalyses(worksheetanalysis_review_state = 'unassigned'):
    return False

return True
