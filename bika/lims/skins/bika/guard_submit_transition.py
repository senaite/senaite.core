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

if context.portal_type == "Analysis":

    # This code was present both here and in AnalysiRequest/WorkflowAction
    # both instances have been commented - ther must be some better method
    # of deferring to our depedencies.

    # dependencies = context.getDependencies()
    # if dependencies:
    #     interim_fields = False
    #     service = context.getService()
    #     calculation = service.getCalculation()
    #     if calculation:
    #         interim_fields = calculation.getInterimFields()
    #     for dep in dependencies:
    #         review_state = workflow.getInfoFor(dep, 'review_state')
    #         if interim_fields:
    #             if review_state in ('to_be_sampled', 'to_be_preserved',
    #                                 'sample_due', 'sample_received',
    #                                 'attachment_due', 'to_be_verified',):
    #                 return False
    #         else:
    #             if review_state in ('to_be_sampled', 'to_be_preserved',
    #                                 'sample_due', 'sample_received',):
    #                 return False

    # State checking
    # If our state is Sample Due, then we permit Submit transition only
    # if the PointOfCapture is 'field'
    if workflow.getInfoFor(context, "review_state") == 'sample_due':
        if context.getPointOfCapture() == "lab":
            return False

    return True

if context.portal_type == "AnalysisRequest":
    # Only transition to 'attachment_due' if all analyses are at least there.
    has_analyses = False
    for a in context.objectValues('Analysis'):
        has_analyses = True
        review_state = workflow.getInfoFor(a, 'review_state')
        if review_state in ('to_be_sampled', 'to_be_preserved',
                            'sample_due', 'sample_received',):
            return False
    return has_analyses

if context.portal_type == "Worksheet":

    if not context.getAnalyst():
        return False

    # Only transition to 'attachment_due' if all analyses are at least there.
    has_analyses = False
    workflow = context.portal_workflow
    for a in context.getAnalyses():
        has_analyses = True
        review_state = workflow.getInfoFor(a, 'review_state', '')
        if review_state in ('sample_received', 'assigned',):
            # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
            return False
    return has_analyses
