## Controller Python Script "batch_status_modify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=None, ids=[], comment='No comment', expiration_date=None, effective_date=None, include_subfolders=0
##title=Change status of ARs in batch
##


from ZODB.POSException import ConflictError
from Products.CMFPlone import transaction_note
rc = context.reference_catalog
wf_tool = context.portal_workflow
review_state = ''
failed = {}
success = {}
if workflow_action == 'publish':
    context.REQUEST.set('PUBLISH_BATCH', 1)

came_from = context.REQUEST.get('came_from', 'analysisrequests')
if came_from == 'analysisrequests':
    status_failure = 'failure_analysisrequests'
    status_success = 'success_analysisrequests'
    if workflow_action == 'receive':
        status_success = 'receive_ars'
        context.REQUEST.SESSION.set('uids', ids)
elif came_from == 'client_analysisrequests':
    status_failure = 'failure_clientars'
    status_success = 'success_clientars'
elif came_from == 'orders':
    status_failure = 'failure_orders'
    status_success = 'success_orders'
elif came_from == 'standardsamples':
    status_failure = 'failure_standards'
    status_success = 'success_standards'
elif came_from == 'samples':
    status_failure = 'failure_samples'
    status_success = 'success_samples'
    if workflow_action == 'receive':
        status_success = 'receive_samples'
        context.REQUEST.SESSION.set('uids', ids)

if not ids:
    return state.set(status=status_failure,
        portal_status_message='You must select content to change.')

if workflow_action == 'assign':
    return state.set(status=status_failure,
        portal_status_message='Cannot assign to worksheet')

for uid in ids:
    o = rc.lookupObject(uid)
    if workflow_action == 'republish':
        success[uid]=o
    else:
        try:
            o.content_status_modify( workflow_action,
                                     comment,
                                     effective_date=effective_date,
                                     expiration_date=expiration_date )
            review_state = wf_tool.getInfoFor(o, 'review_state', '')
            success[uid]=o
        except ConflictError:
            raise
        except Exception, e:
            failed[uid]=e

    transaction_note( str(ids) + ' transitioned ' + workflow_action )
if review_state:
    context.REQUEST.SESSION.set('review_state', review_state)

if workflow_action in ['publish', 'republish']:
    ars = success.values()
    context.publish_batch(ars)

    # perform print publish batch - must be done after all others published
    print_ids = []
    for ar in ars:
        contact = ar.getContact()
        if 'print' in contact.getPublicationPreference():
            print_ids.append(ar.UID())
    if len(print_ids) > 0:
        context.REQUEST.SESSION.set('uids', print_ids)
        status_success = 'print_ars'

# clear the 'content modified' messages that have been added for each AR
msgs = context.plone_utils.showPortalMessages()
if workflow_action != 'republish':
    context.plone_utils.addPortalMessage(u'Your content\'s status has been modified')
# It is necessary to set the context to override context from
# content_status_modify
return state.set(context=context, status=status_success,
    portal_status_message='Content has been changed')

