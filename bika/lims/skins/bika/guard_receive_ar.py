## Script (Python) "guard_receive_ar"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from DateTime import DateTime
wf_tool = context.portal_workflow

# Can't receive if AR is cancelled
if wf_tool.getInfoFor(context, 'cancellation_state') == "cancelled":
    return False

# Can't receive if our sample's DateSampled is the future
if context.getSample().getDateSampled() > DateTime():
    return False

return True

