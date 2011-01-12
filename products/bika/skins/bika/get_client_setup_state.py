## Script (Python) "get_client_setup_state"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Determine whether client actions or setup should be shown
##

session = context.REQUEST.SESSION

key = 'client_setup_state'
if session.has_key(key):
    if session[key] == 'setup':
        return 'setup'
    else:
        return 'actions'
else:
    session.set(key, 'actions')
    return 'actions'
