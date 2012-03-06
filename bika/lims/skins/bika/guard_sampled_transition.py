## Script (Python) "guard_sampled_transition"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##

from DateTime import DateTime
workflow = context.portal_workflow

# If sampling_workflow_enabled is not set, this transition is not available.
props = context.portal_properties.bika_properties
if not props.getProperty('sampling_workflow_enabled', True):
    return False

# False if object is cancelled
if workflow.getInfoFor(context, 'cancellation_state', "active") == "cancelled":
    return False

# (Sample Partiton shares the Sample Workflow, so this guard is called)
# Transition is always available on SamplePartition objects
if context.portal_type == 'SamplePartition':
    return True

if context.portal_type == 'AnalysisRequest':

    # False if this sample has been "sampled"
    if context.getSample().getDateSampled():
        return False

    # False if our SamplingDate is the future
    if context.getSample().getSamplingDate() > DateTime():
        return False

elif context.portal_type == 'Sample':

    # False if this sample has been "sampled"
    if context.getDateSampled():
        return False

    # False if our SamplingDate is the future
    if context.getSamplingDate() > DateTime():
        return False

return True
