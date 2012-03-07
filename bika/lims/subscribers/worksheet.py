from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def AfterTransitionEventHandler(ws, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    if event.transition.id == "attach":
        # Need a separate skiplist for this due to double-jumps with 'submit'.
        if not ws.REQUEST.has_key('workflow_attach_skiplist'):
            ws.REQUEST['workflow_attach_skiplist'] = [ws.UID(), ]
        else:
            if ws.UID() in ws.REQUEST['workflow_attach_skiplist']:
                logger.info("WS Skip")
                return
            else:
                ws.REQUEST["workflow_attach_skiplist"].append(ws.UID())

        logger.info("Starting: %s on %s" % (event.transition.id, ws))

        ws.reindexObject(idxs = ["review_state", ])
        # Don't cascade. Shouldn't be attaching WSs for now (if ever).
        return

    if not ws.REQUEST.has_key('workflow_skiplist'):
        ws.REQUEST['workflow_skiplist'] = [ws.UID(), ]
    else:
        if ws.UID() in ws.REQUEST['workflow_skiplist']:
            logger.info("WS Skip")
            return
        else:
            ws.REQUEST["workflow_skiplist"].append(ws.UID())

    logger.info("Starting: %s on %s" % (event.transition.id, ws))

    wf = getToolByName(ws, 'portal_workflow')

    if event.transition.id == "submit":
        # Don't cascade. Shouldn't be submitting WSs directly for now,
        # except edge cases where all analyses are already submitted,
        # but WS was held back until an analyst was assigned.
        ws.reindexObject(idxs = ["review_state", ])
        can_attach = True
        for a in ws.getAnalyses():
            if wf.getInfoFor(a, 'review_state') in \
               ('to_be_sampled', 'to_be_preserved', 'sample_due',
                'sample_received', 'attachment_due', 'assigned',):
                # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
                can_attach = False
                break
        if can_attach:
            wf.doActionFor(ws, 'attach')

    elif event.transition.id == "retract":
        ws.reindexObject(idxs = ["review_state", ])
        if not "retract all analyses" in ws.REQUEST['workflow_skiplist']:
            # retract all analyses in this WS.
            # (NB: don't retract if it's verified)
            analyses = ws.getAnalyses()
            for analysis in analyses:
                if wf.getInfoFor(analysis, 'review_state', '') not in ('attachment_due', 'to_be_verified',):
                    continue
                if not analysis.UID in ws.REQUEST['workflow_skiplist']:
                    wf.doActionFor(analysis, 'retract')

    elif event.transition.id == "verify":
        ws.reindexObject(idxs = ["review_state", ])
        if not "verify all analyses" in ws.REQUEST['workflow_skiplist']:
            # verify all analyses in this WS.
            analyses = ws.getAnalyses()
            for analysis in analyses:
                if wf.getInfoFor(analysis, 'review_state', '') != 'to_be_verified':
                    continue
                if not analysis.UID in ws.REQUEST['workflow_skiplist']:
                    wf.doActionFor(analysis, "verify")

    return
