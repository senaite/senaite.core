## Script (Python) "guard_preserved_transition"
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

# False if object is cancelled
if workflow.getInfoFor(context, 'cancellation_state', "active") == "cancelled":
    return False

# A sample can't be "preserved" until all it's partitions are sample_due
# ie, sampling and/or preservation completed.
if [sp for sp in context.objectValues("SamplePartition")
    if workflow.getInfoFor(sp, 'review_state') != 'sample_due']:
    return False

return True
