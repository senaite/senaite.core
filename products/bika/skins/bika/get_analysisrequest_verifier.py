## Script (Python) "get_analysisrequest_verifier"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=analysisrequest
##title=Get analysis workflow states
##

## get the name of the member who last verified this AR
##  (better to reverse list and get first!)

wtool = context.portal_workflow
mtool = context.portal_membership


verifier = None
try:
    review_history = wtool.getInfoFor(analysisrequest, 'review_history')
except:
    return 'access denied'

[review for review in review_history if review.get('action','')]
if not review_history:
    return 'no history'
for items in  review_history:
    action = items.get('action')
    if action != 'verify':
        continue
    actor = items.get('actor')
    member = mtool.getMemberById(actor)
    verifier = member.getProperty('fullname')
    if verifier is None or verifier == '':
        verifier = actor                                          
return verifier
