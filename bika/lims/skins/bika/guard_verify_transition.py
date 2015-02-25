## Script (Python) "guard_verify_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from AccessControl import getSecurityManager
from bika.lims.permissions import Verify, VerifyOwnResults

workflow = context.portal_workflow
checkPermission = context.portal_membership.checkPermission

# Can't do anything to the object if it's cancelled
# reference and duplicate analyses don't have cancellation_state
#if context.portal_type == "Analysis":
if workflow.getInfoFor(context, 'cancellation_state', 'active') == "cancelled":
    return False

# All kinds of analyses get their submitter and verifier compared
if context.portal_type in ("ReferenceAnalysis",
                           "DuplicateAnalysis"):

    # May we verify results that we ourself submitted?
    if checkPermission(VerifyOwnResults, context):
        return True

    # Check for self-submitted Analysis.
    user_id = getSecurityManager().getUser().getId()
    self_submitted = False
    review_history = workflow.getInfoFor(context, 'review_history')
    review_history = context.reverseList(review_history)
    for event in review_history:
        if event.get('action') == 'submit':
            if event.get('actor') == user_id:
                self_submitted = True
            break
    if self_submitted:
        return False

if context.portal_type == "AnalysisRequest":

    if not checkPermission(Verify, context):
        # Allow automatic verify (Disregard permission)
        # if all analyses are already verified.
        for analysis in context.getAnalyses(full_objects = True):
            review_state = workflow.getInfoFor(analysis, 'review_state')
            if review_state in ('to_be_sampled', 'to_be_preserved',
                                'sample_due', 'sample_received',
                                'attachment_due', 'to_be_verified'):
                return False
        return True

    # May we verify results that we ourself submitted?
    if checkPermission(VerifyOwnResults, context):
        return True

    # Check for self-submitted Analysis.
    user_id = getSecurityManager().getUser().getId()
    self_submitted = False
    for analysis in context.getAnalyses(full_objects = True):
        review_state = workflow.getInfoFor(analysis, 'review_state')
        if review_state == 'to_be_verified':
            review_history = workflow.getInfoFor(analysis, 'review_history')
            review_history = context.reverseList(review_history)
            for event in review_history:
                if event.get('action') == 'submit':
                    if event.get('actor') == user_id:
                        self_submitted = True
                    break
            if self_submitted:
                break
    if self_submitted:
        return False

if context.portal_type == "Worksheet":

    if not checkPermission(Verify, context):
        # Allow automatic verify (Disregard permission)
        # if all analyses are already verified.
        for analysis in context.getAnalyses(full_objects = True):
            review_state = workflow.getInfoFor(analysis, 'review_state')
            if review_state in ('sample_received', 'attachment_due', 'to_be_verified'):
                return False
        return True

    # May we verify results that we ourself submitted?
    if checkPermission(VerifyOwnResults, context):
        return True

    # Check for self-submitted analyses.
    user_id = getSecurityManager().getUser().getId()
    self_submitted = False
    for analysis in context.getAnalyses():
        review_state = workflow.getInfoFor(analysis, 'review_state')
        if review_state == 'to_be_verified':
            review_history = workflow.getInfoFor(analysis, 'review_history')
            review_history = context.reverseList(review_history)
            for event in review_history:
                if event.get('action') == 'submit':
                    if event.get('actor') == user_id:
                        self_submitted = True
                    break
            if self_submitted:
                break
    if self_submitted:
        return False

return True

