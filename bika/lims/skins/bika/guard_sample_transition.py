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

# False if object is cancelled
if workflow.getInfoFor(context, 'cancellation_state', "active") == "cancelled":
    return False

return True
