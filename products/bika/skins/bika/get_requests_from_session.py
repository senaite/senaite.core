## Script (Python) "get_requests_from_session"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get analysis requests by resolving uids on session
##

rc = context.reference_catalog
session = context.REQUEST.SESSION
results = [rc.lookupObject(uid) for uid in session.get('uids', [])]
sort_on = (('id', 'nocase', 'desc'),)
results = sequence.sort(results, sort_on)

return results
