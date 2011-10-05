## Script (Python) "guard_receive_sample"
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

# Can't receive if DateSampled is the future
if wf_tool.getInfoFor(context, 'cancellation_state') == "cancelled":
    return False
else:
    if context.getDateSampled() > DateTime():
        return False

return True

