## Script (Python) "guard_cancelled_object"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

workflow = context.portal_workflow

# Note: Also used by profiles/default/types/AnalysisRequest.xml

# Can't do anything to the object if it's cancelled
if workflow.getInfoFor(context, 'cancellation_state', "active") == "cancelled":
    return False

return True
