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

SamplingWorkflowEnabled = context.bika_setup.getSamplingWorkflowEnabled()

return SamplingWorkflowEnabled and True or False

