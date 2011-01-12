## Script (Python) "sort_analyses_on_requestid"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=analyses
##title=
##
r = {}
for a in analyses:
    ar_id = a.aq_parent.getRequestID()
    l = r.get(ar_id, [])
    l.append(a)
    r[ar_id] = l

k = r.keys()
k.sort()
result = []
for ar_id in k:
    result += r[ar_id]
    
return result
