## Controller Python Script "assign_to_worksheet"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[], comment='No comment', expiration_date=None, effective_date=None, include_subfolders=0
##title=Assign ARs to worksheet in batch
##

from ZODB.POSException import ConflictError
from Products.CMFPlone import transaction_note
rc = context.reference_catalog
failed = {}
success = {}
workflow_action = 'assign'
wf_tool = context.portal_workflow
review_state = ''

if not ids:
    return state.set(status='failure',
        portal_status_message='You must select content to change.')

worksheet_id = context.worksheets.generateUniqueId('Worksheet')
context.worksheets.invokeFactory(id=worksheet_id, type_name='Worksheet')
worksheet = context.worksheets[worksheet_id]

for uid in ids:
    o = rc.lookupObject(uid)
    worksheet.assignAnalyses(Analyses=[a.UID() for a in o.getAnalyses()]) 
    try:
        o.content_status_modify( workflow_action,
                                comment,
                                effective_date=effective_date,
                                expiration_date=expiration_date )
        review_state = wf_tool.getInfoFor(o, 'review_state', '')
        success[id]=comment
    except ConflictError:
        raise
    except Exception, e:
        failed[id]=e

transaction_note( str(ids) + ' transitioned ' + workflow_action )
if review_state:
    context.REQUEST.SESSION.set('review_state', review_state)

# It is necessary to set the context to override context from
# content_status_modify
return state.set(context=context,
    portal_status_message='Content has been changed.')
