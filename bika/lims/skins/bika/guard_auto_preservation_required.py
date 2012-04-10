## Script (Python) "guard_auto_preservation_required"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##

# Automatic transition that fires when object enters "Sampled" state
# If this guard returns True, the object will transition to to_be_preserved.
# If the guard returns False, the object will be transitioned to sample_due.

from DateTime import DateTime
workflow = context.portal_workflow

if context.portal_type == 'Sample':

    # If none of this sample's partitions require preservation, then we return
    # false.
    preservation_required = False
    for part in context.objectValues("SamplePartition"):
        if part.getPreservation():
            preservation_required = True
            break
    return preservation_required

elif context.portal_type == 'AnalysisRequest':

    # If none of this sample's partitions require preservation, then we return
    # false.
    sample = context.getSample()
    preservation_required = False
    for part in sample.objectValues("SamplePartition"):
        if part.getPreservation():
            preservation_required = True
            break
    return preservation_required

elif context.portal_type == 'SamplePartition':

    if context.getPreservation():
        return True
    else:
        return False

elif context.portal_type == 'Analysis':

    if context.getSamplePartition().getPreservation():
        return True
    else:
        return False
