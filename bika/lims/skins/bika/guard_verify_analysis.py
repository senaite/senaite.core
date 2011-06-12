## Script (Python) "guard_verify_analysis"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##

# Manager may always verify
checkPermission = context.portal_membership.checkPermission
if checkPermission('Manage portal', context):
    return 1
    
# get the current state of analyses guard errors
if context.REQUEST.has_key('GuardError'):
    guard_error = context.REQUEST['GuardError'] 
else:
    guard_error = 'None'
from AccessControl import getSecurityManager
user_id = getSecurityManager().getUser().getId()
wf_tool = context.portal_workflow

if context.portal_type == 'Analysis':
    if not context.getAttachment():
        if context.bika_settings.settings.getAnalysisAttachmentsPermitted():
            service = context.getService()
            if service.getAttachmentOption() == 'r':
                return 0

    if context.getCalcType() == 'dep':
        return 1
    self_submitted = False
    review_history = wf_tool.getInfoFor(context, 'review_history')
    review_history = context.reverseList(review_history)
    for event in review_history:
        if event.get('action') == 'submit':
            if event.get('actor') == user_id:
                self_submitted = True
            break
    if self_submitted:
        if guard_error == 'None':
            context.REQUEST.set('GuardError', 'Fail')
        elif guard_error == 'Pass':
            context.REQUEST.set('GuardError', 'Partial')
        return 0
    else:
        if guard_error == 'None':
            context.REQUEST.set('GuardError', 'Pass')
        elif guard_error == 'Fail':
            context.REQUEST.set('GuardError', 'Partial')
        return 1
elif context.portal_type == 'AnalysisRequest':
    if not context.getAttachment():
        if context.bika_settings.settings.getARAttachmentOption() == 'r':
            return 0
    self_submitted = False
    for analysis in context.getAnalyses():
        if not analysis.getAttachment():
            service = analysis.getService()
            if service.getAttachmentOption() == 'r':
                return 0

        if analysis.getCalcType() == 'dep':
            continue
        review_state = wf_tool.getInfoFor(analysis, 'review_state')
        if review_state == 'to_be_verified': 
            review_history = wf_tool.getInfoFor(analysis, 'review_history')
            review_history = context.reverseList(review_history)
            for event in review_history:
                if event.get('action') == 'submit':
                    if event.get('actor') == user_id:
                        self_submitted = True
                    break
            if self_submitted:
                break
    if self_submitted:
        return 0
    else:
        return 1

