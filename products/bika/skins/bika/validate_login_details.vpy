## Controller Python Script "validate_lims_access"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=username='',email='',password='',confirm=''
##title=validates username and password

reg_tool=context.portal_registration
def missing(field):
    state.setError(field, 'Input is required but no input given.', 'input_required')
def nomatch(field):
    state.setError(field, 'Passwords do not match.', 'nomatch_password')
def minlimit(field):
    state.setError(field, 'Passwords must contain at least 5 letters.', 'min_password')

if not username:
    missing('username')
if not email:
    missing('email')

properties = context.portal_properties.site_properties
if not properties.validate_email:
     if password!=confirm:
         nomatch('password')
         nomatch('confirm')

     if not password:
         missing('password')
     if not confirm:
         missing('confirm')

     if not state.getError('password') and len(password) < 5:
         minlimit('password')
         minlimit('confirm')

if not state.getError('username') and not reg_tool.isMemberIdAllowed(username):
    state.setError('username',
                   'The login name you selected is already in use or is not valid. Please choose another.',
                   'username_invalid' )

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state.set(portal_status_message='The user was successfully created.')
