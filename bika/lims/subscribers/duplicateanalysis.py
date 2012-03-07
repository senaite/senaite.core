from AccessControl import getSecurityManager
from Products.Archetypes.config import REFERENCE_CATALOG
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
import transaction


def AfterTransitionEventHandler(analysis, event):

    # Note: Don't have dependencies or dependents, not on an AR
    #----------------------------------------------------------

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    if event.transition.id == "attach":
        # Need a separate skiplist for this due to double-jumps with 'submit'.
        if not analysis.REQUEST.has_key('workflow_attach_skiplist'):
            analysis.REQUEST['workflow_attach_skiplist'] = [analysis.UID(), ]
        else:
            if analysis.UID() in analysis.REQUEST['workflow_attach_skiplist']:
                logger.info("dup Skip")
                return
            else:
                analysis.REQUEST["workflow_attach_skiplist"].append(analysis.UID())

        logger.info("Starting: %s on dup %s" % (event.transition.id, analysis.getService().getKeyword()))

        wf = getToolByName(analysis, 'portal_workflow')
        analysis.reindexObject(idxs = ["review_state", ])

        # If all analyses on the worksheet have been attached,
        # then attach the worksheet.
        ws = analysis.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = wf.getInfoFor(ws, 'review_state')
        if (ws_state == 'attachment_due'
        and ws.UID() not in analysis.REQUEST['workflow_attach_skiplist']):
            can_attach = True
            for a in ws.getAnalyses():
                if wf.getInfoFor(a, 'review_state') in \
                   ('to_be_sampled', 'to_be_preserved', 'sample_due',
                    'sample_received', 'attachment_due', 'assigned',):
                    can_attach = False
                    break
            if can_attach:
                wf.doActionFor(ws, 'attach')

        return

    #------------------------------------------------------
    # End of "attach" code, back to your basic nightmare...
    #------------------------------------------------------

    if not analysis.REQUEST.has_key('workflow_skiplist'):
        analysis.REQUEST['workflow_skiplist'] = [analysis.UID(), ]
    else:
        if analysis.UID() in analysis.REQUEST['workflow_skiplist']:
            logger.info("dup Skip")
            return
        else:
            analysis.REQUEST["workflow_skiplist"].append(analysis.UID())

    logger.info("Starting: %s on dup %s" % (event.transition.id, analysis.getService().getKeyword()))

    wf = getToolByName(analysis, 'portal_workflow')

    if event.transition.id == "submit":
        analysis.reindexObject(idxs = ["review_state", ])

        # If all analyses on the worksheet have been submitted,
        # then submit the worksheet.
        ws = analysis.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        # if the worksheet analyst is not assigned, the worksheet can't  be transitioned.
        if ws.getAnalyst() and ws.UID() not in analysis.REQUEST['workflow_skiplist']:
            all_submitted = True
            for a in ws.getAnalyses():
                if wf.getInfoFor(a, 'review_state') in \
                   ('to_be_sampled', 'to_be_preserved', 'sample_due',
                    'sample_received', 'assigned',):
                    all_submitted = False
                    break
            if all_submitted:
                wf.doActionFor(ws, 'submit')

        # If no problem with attachments, do 'attach' action for this analysis.
        can_attach = True
        if not analysis.getAttachment():
            service = analysis.getService()
            if service.getAttachmentOption() == 'r':
                can_attach = False
        if can_attach:
            wf.doActionFor(analysis, 'attach')

    elif event.transition.id == "retract":
        analysis.reindexObject(idxs = ["review_state", ])
        # Escalate action to the Worksheet.
        ws = analysis.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        if not ws.UID() in analysis.REQUEST['workflow_skiplist']:
            if wf.getInfoFor(ws, 'review_state') == 'open':
                analysis.REQUEST["workflow_skiplist"].append(ws.UID())
            else:
                if not "retract all analyses" in analysis.REQUEST['workflow_skiplist']:
                    analysis.REQUEST["workflow_skiplist"].append("retract all analyses")
                wf.doActionFor(ws, 'retract')

    elif event.transition.id == "verify":
        analysis.reindexObject(idxs = ["review_state", ])

        # If all other analyses on the worksheet are verified,
        # then verify the worksheet.
        ws = analysis.getBackReferences('WorksheetAnalysis')
        ws = ws[0]
        ws_state = wf.getInfoFor(ws, 'review_state')
        if (ws_state == 'to_be_verified'
        and ws.UID() not in analysis.REQUEST['workflow_skiplist']):
            all_verified = True
            for a in ws.getAnalyses():
                if wf.getInfoFor(a, 'review_state') in \
                   ('to_be_sampled', 'to_be_preserved', 'sample_due',
                    'sample_received', 'attachment_due', 'to_be_verified', 'assigned'):
                    all_verified = False
                    break
            if all_verified:
                if not "verify all analyses" in analysis.REQUEST['workflow_skiplist']:
                    analysis.REQUEST["workflow_skiplist"].append("verify all analyses")
                wf.doActionFor(ws, "verify")

    elif event.transition.id == "assign":
        analysis.reindexObject(idxs = ["review_state", ])
        rc = getToolByName(analysis, REFERENCE_CATALOG)
        wsUID = analysis.REQUEST['context_uid']
        ws = rc.lookupObject(wsUID)

        # retract the worksheet to 'open'
        ws_state = wf.getInfoFor(ws, 'review_state')
        if ws_state != 'open':
            if not analysis.REQUEST.has_key('workflow_skiplist'):
                analysis.REQUEST['workflow_skiplist'] = ['retract all analyses', ]
            else:
                analysis.REQUEST["workflow_skiplist"].append('retract all analyses')
            wf.doActionFor(ws, 'retract')

    elif event.transition.id == "unassign":
        analysis.reindexObject(idxs = ["review_state", ])
        rc = getToolByName(analysis, REFERENCE_CATALOG)
        wsUID = analysis.REQUEST['context_uid']
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
        #       to allow multiple promotions (maybe by more than one analysis).
            if can_submit and wf.getInfoFor(ws, 'review_state') == 'open':
                wf.doActionFor(ws, 'submit')
                analysis.REQUEST["workflow_skiplist"].remove(wsUID)
            if can_attach and wf.getInfoFor(ws, 'review_state') == 'attachment_due':
                wf.doActionFor(ws, 'attach')
                analysis.REQUEST["workflow_attach_skiplist"].remove(wsUID)
            if can_verify and wf.getInfoFor(ws, 'review_state') == 'to_be_verified':
                analysis.REQUEST["workflow_skiplist"].append('verify all analyses')
                wf.doActionFor(ws, 'verify')
                analysis.REQUEST["workflow_skiplist"].remove(wsUID)
        else:
            if wf.getInfoFor(ws, 'review_state') != 'open':
                wf.doActionFor(ws, 'retract')
                analysis.REQUEST["workflow_skiplist"].remove(wsUID)

    return
