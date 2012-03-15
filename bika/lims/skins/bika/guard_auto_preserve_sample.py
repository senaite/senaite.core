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

# Prevent auto-transition if any of our partitions are not yet sample_due
if context.portal_type == "Sample":
    for part in context.objectValues("SamplePartition"):
        if workflow.getInfoFor(part, "review_state") == 'to_be_preserved':
            return False

return True