## Script (Python) "validate_integrity"
##title=Validate Integrity
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##
errors = {}
errors = context.validate(REQUEST=context.REQUEST, errors=errors, data=1, metadata=0)

if errors:
    return state.set(status='failure', errors=errors, portal_status_message='Please correct the indicated errors.')
else:
    return state.set(status='success', portal_status_message='Your changes have been saved.')
