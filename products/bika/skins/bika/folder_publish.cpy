## Controller Python Script "folder_publish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=workflow_action=None, ids=[], comment='No comment', expiration_date=None, effective_date=None, include_subfolders=0
##title=Publish objects from a folder
##

from ZODB.POSException import ConflictError
from Products.CMFPlone import transaction_note
plone_utils=context.plone_utils
REQUEST=context.REQUEST
workflow = context.portal_workflow
content_status_modify=context.content_status_modify
failed = {}
success = {}

if workflow_action is None:
    return state.set(status='failure', portal_status_message='You must select a publishing action.')
if not ids:
    return state.set(status='failure', portal_status_message='You must select content to change.')

for id in ids:
    o = getattr(context, id)
    try:
        if o.isPrincipiaFolderish and include_subfolders:
            # call the script to do the workflow action
            # catch it if there is not workflow action for this object
            # but continue with subobjects.
            # Since we can have mixed portal_type objects it can occur
            # quite easily that the workflow_action doesn't work for some objects
            # but we need to keep on going.
            try:
                o.content_status_modify( workflow_action,
                                         comment,
                                         effective_date=effective_date,
                                         expiration_date=expiration_date )
            except ConflictError:
                raise
            except Exception, e:
                # skip this object but continue with sub-objects.
                failed[id]=e
            
            o.folder_publish( workflow_action, 
                              o.objectIds(), 
                              comment=comment, 
                              include_subfolders=include_subfolders, 
                              effective_date=effective_date,
                              expiration_date=expiration_date )
        else:
            o.content_status_modify( workflow_action,
                                     comment,
                                     effective_date=effective_date,
                                     expiration_date=expiration_date )
            success[id]=comment
    except ConflictError:
        raise
    except Exception, e:
        failed[id]=e

# if only some analyses were published we still send an email
if workflow_action in ['publish', 'republish', 'prepublish'] and \
        context.portal_type == 'AnalysisRequest' and \
        len(success.keys()) > 0:
    contact = context.getContact()
    analysis_requests = [context]
    contact.publish_analysis_requests(contact, analysis_requests, None)
    # cc contacts
    for cc_contact in context.getCCContact():
        contact.publish_analysis_requests(cc_contact, analysis_requests, None)
    # cc emails
    cc_emails = context.getCCEmails()
    if cc_emails:
        contact.publish_analysis_requests(None, analysis_requests, cc_emails)


transaction_note( str(ids) + ' transitioned ' + workflow_action )

# It is necessary to set the context to override context from content_status_modify
portal_message = 'Content has been changed'
# Determine whether only partial content has been changed
if context.REQUEST.form.has_key('GuardError'):
    guard_error = context.REQUEST['GuardError']
    if guard_error == 'Fail':
        portal_message = 'Content has not been changed'
    elif guard_error == 'Partial':
        portal_message = 'Some content has been changed'
        
return state.set(context=context, portal_status_message=portal_message)
