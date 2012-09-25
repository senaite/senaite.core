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

# Pre-preserved containers are short-circuited here.

# Returning a value other than True or False will leave the context in
# "sampled" state

from DateTime import DateTime
workflow = context.portal_workflow

if context.portal_type == 'Sample':

    parts = context.objectValues("SamplePartition")
    if not parts:
        # AR is being created - AR Add will transition us.
        return None

    # If none of this sample's partitions require preservation, then we return
    # false.
    preservation_required = False
    for part in parts:
        if part.getPreservation():
            if part.getContainer() \
               and part.getContainer().getPrePreserved():
                preservation_required = False
            else:
                preservation_required = True
            break
    return preservation_required

elif context.portal_type == 'AnalysisRequest':

    sample = context.getSample()
    if not sample:
        # AR is being created - AR Add will transition us.
        return None

    # If none of this sample's partitions require preservation, then we return
    # false.
    preservation_required = False
    for part in sample.objectValues("SamplePartition"):
        if part.getPreservation():
            if part.getContainer() \
               and part.getContainer().getPrePreserved():
                preservation_required = False
            else:
                preservation_required = True
            break
    return preservation_required

elif context.portal_type == 'SamplePartition':

    analyses = context.getBackReferences('AnalysisSamplePartition')
    if not analyses:
        # AR is being created - AR Add will transition us.
        return None

    if context.getPreservation():
        if context.getContainer() \
           and context.getContainer().getPrePreserved():
            return False
        else:
            return True
    else:
        return False

elif context.portal_type == 'Analysis':

    part = context.getSamplePartition()
    if not part:
        # AR is being created - AR Add will transition us.
        return None
    part = context.getSamplePartition()
    if part.getPreservation():
        if part.getContainer() \
           and part.getContainer().getPrePreserved():
            return False
        else:
            return True
    else:
        return False
