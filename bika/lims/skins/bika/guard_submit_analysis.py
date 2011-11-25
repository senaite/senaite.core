## Script (Python) "guard_submit_analysis"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

wf_tool = context.portal_workflow

# Can't do anything to the object if it's cancelled
if wf_tool.getInfoFor(context, 'cancellation_state') == "cancelled":
    return False

dependencies = context.getDependencies()
if dependencies:
    interim_fields = False
    service = context.getService()
    calculation = service.getCalculation()
    if calculation:
        interim_fields = calculation.getInterimFields()
    for dep in dependencies:
        review_state = wf_tool.getInfoFor(dep, 'review_state')
        if interim_fields:
            if review_state in ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
                return False
        else:
            if review_state in ('sample_due', 'sample_received',):
                return False
return True

