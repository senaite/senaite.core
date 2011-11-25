## Script (Python) "guard_cancelled_object"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

wf_tool = context.portal_workflow

# Note: Used by profiles/default/types/AnalysisRequest.xml as well as workflows.

# Can't do anything to the object if it's cancelled
if wf_tool.getInfoFor(context, 'cancellation_state') == "cancelled":
    return False

return True

