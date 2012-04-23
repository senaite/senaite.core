from AccessControl import getSecurityManager
from Products.Archetypes.config import REFERENCE_CATALOG
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
import transaction

def AfterTransitionEventHandler(instance, event):

    # Note: Don't have dependencies or dependents, not on an AR
    #----------------------------------------------------------

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    action_id = event.transition.id

    if skip(instance, action_id):
        return

    if action_id == "attach":
        wf = getToolByName(instance, 'portal_workflow')
        instance.reindexObject(idxs = ["review_state", ])

        # If all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = instance.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = wf.getInfoFor(ws, 'review_state')
        if ws_state == 'attachment_due' and not skip(ws, action_id, peek=True):
            can_attach = True
            for a in ws.getAnalyses():
                if wf.getInfoFor(a, 'review_state') in \
                   ('sample_due', 'sample_received', 'attachment_due', 'assigned',):
                    can_attach = False
                    break
            if can_attach:
                wf.doActionFor(ws, 'attach')

        return

    #------------------------------------------------------
    # End of "attach" code, back to your basic nightmare...
    #------------------------------------------------------

    wf = getToolByName(instance, 'portal_workflow')

    if action_id == "submit":
        instance.reindexObject(idxs = ["review_state", ])

        # If all analyses on the worksheet have been submitted,
        # then submit the worksheet.
        ws = instance.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        # if the worksheet analyst is not assigned, the worksheet can't  be transitioned.
        if ws.getAnalyst() and not skip(ws, action_id, peek=True):
            all_submitted = True
            for a in ws.getAnalyses():
                if wf.getInfoFor(a, 'review_state') in \
                   ('sample_due', 'sample_received', 'assigned',):
                    all_submitted = False
                    break
            if all_submitted:
                wf.doActionFor(ws, 'submit')

        # If no problem with attachments, do 'attach' action for this instance.
        can_attach = True
        if not instance.getAttachment():
            service = instance.getService()
            if service.getAttachmentOption() == 'r':
                can_attach = False
        if can_attach:
            wf.doActionFor(instance, 'attach')

    elif action_id == "retract":
        instance.reindexObject(idxs = ["review_state", ])
        # Escalate action to the Worksheet.
        ws = instance.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        if not skip(ws, action_id, peek=True):
            if wf.getInfoFor(ws, 'review_state') == 'open':
                skip(ws, action_id)
            else:
                if not "retract all analyses" in instance.REQUEST['workflow_skiplist']:
                    instance.REQUEST["workflow_skiplist"].append("retract all analyses")
                wf.doActionFor(ws, 'retract')

    elif action_id == "verify":
        instance.reindexObject(idxs = ["review_state", ])

        # If all other analyses on the worksheet are verified,
        # then verify the worksheet.
        ws = instance.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = wf.getInfoFor(ws, 'review_state')
        if ws_state == 'to_be_verified' and not skip(ws, action_id, peek=True):
            all_verified = True
            for a in ws.getAnalyses():
                if wf.getInfoFor(a, 'review_state') in \
                   ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified', 'assigned'):
                    all_verified = False
                    break
            if all_verified:
                if not "verify all analyses" in instance.REQUEST['workflow_skiplist']:
                    instance.REQUEST["workflow_skiplist"].append("verify all analyses")
                wf.doActionFor(ws, "verify")

    elif action_id == "assign":
        instance.reindexObject(idxs = ["review_state", ])
        rc = getToolByName(instance, REFERENCE_CATALOG)
        wsUID = instance.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # retract the worksheet to 'open'
        ws_state = wf.getInfoFor(ws, 'review_state')
        if ws_state != 'open':
            if not instance.REQUEST.has_key('workflow_skiplist'):
                instance.REQUEST['workflow_skiplist'] = ['retract all analyses', ]
            else:
                instance.REQUEST["workflow_skiplist"].append('retract all analyses')
            wf.doActionFor(ws, 'retract')

    elif action_id == "unassign":
        instance.reindexObject(idxs = ["review_state", ])
        rc = getToolByName(instance, REFERENCE_CATALOG)
        wsUID = instance.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # May need to promote the Worksheet's review_state
        #  if all other analyses are at a higher state than this one was.
        # (or maybe retract it if there are no analyses left)
        # Note: duplicates, controls and blanks have 'assigned' as a review_state.
        can_submit = True
        can_attach = True
        can_verify = True
        ws_empty = True

        for a in ws.getAnalyses():
            ws_empty = False
            a_state = wf.getInfoFor(a, 'review_state')
            if a_state in \
               ('assigned', 'sample_due', 'sample_received',):
                can_submit = False
            else:
                if not ws.getAnalyst():
                    can_submit = False
            if a_state in \
               ('assigned', 'sample_due', 'sample_received', 'attachment_due',):
                can_attach = False
            if a_state in \
               ('assigned', 'sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
                can_verify = False

        if not ws_empty:
        # Note: WS adds itself to the skiplist so we have to take it off again
        #       to allow multiple promotions (maybe by more than one instance).
            if can_submit and wf.getInfoFor(ws, 'review_state') == 'open':
                wf.doActionFor(ws, 'submit')
                unskip(ws, 'submit', unskip=True)
            if can_attach and wf.getInfoFor(ws, 'review_state') == 'attachment_due':
                wf.doActionFor(ws, 'attach')
                unskip(ws, 'attach', unskip=True)
            if can_verify and wf.getInfoFor(ws, 'review_state') == 'to_be_verified':
                instance.REQUEST["workflow_skiplist"].append('verify all analyses')
                wf.doActionFor(ws, 'verify')
                unskip(ws, 'verify', unskip=True)
        else:
            if wf.getInfoFor(ws, 'review_state') != 'open':
                wf.doActionFor(ws, 'retract')
                unskip(ws, 'retract', unskip=True)

    return
