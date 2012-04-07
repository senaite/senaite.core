## Script (Python) "guard_auto_preserve_sample"
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

# Return TRUE if object advances to To Be Sampled
# Return FALSE if object advances to Sample Due
# We made it a seperate guard, so that ARs and Analyses can depend
# on Sample.getSamplingWorkflowEnabled setting

SamplingWorkflowEnabled = context.bika_setup.getSamplingWorkflowEnabled()

if context.portal_type == 'Sample':
    return SamplingWorkflowEnabled

elif context.portal_type == "AnalysisRequest":
    sample = context.getSample()
    if sample:
        return sample.getSamplingWorkflowEnabled()
    else:
        return SamplingWorkflowEnabled

elif context.portal_type == "Analysis":
    sample = context.aq_parent.getSample()
    if sample:
        return sample.getSamplingWorkflowEnabled()
    else:
        return SamplingWorkflowEnabled

