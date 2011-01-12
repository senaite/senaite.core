## Script (Python) "toggle_state"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=key, default
##title=Toggle state on session for key
##

request = context.REQUEST
session = request.SESSION

if request.has_key(key):
    session.set(key, request.get(key))
elif session.has_key(key):
    request.set(key, session.get(key))
else:
    request.set(key, default)
