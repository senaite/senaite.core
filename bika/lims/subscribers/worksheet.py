from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ActionSucceededEventHandler(ws, event):

    if event.action == "attach":
        # Need a separate skiplist for this due to double-jumps with 'submit'.
        if not ws.REQUEST.has_key('workflow_attach_skiplist'):
            ws.REQUEST['workflow_attach_skiplist'] = [ws.UID(), ]
        else:
            if ws.UID() in ws.REQUEST['workflow_attach_skiplist']:
                logger.info("WS Skip")
                return
            else:
                ws.REQUEST["workflow_attach_skiplist"].append(ws.UID())

        logger.info("Starting: %s on %s" % (event.action, ws))

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

    logger.info("Starting: %s on %s" % (event.action, ws))

    wf = getToolByName(ws, 'portal_workflow')

    if event.action == "submit":
        ws.reindexObject(idxs = ["review_state", ])
        # Don't cascade. Shouldn't be submitting WSs directly for now.

    elif event.action == "retract":
        ws.reindexObject(idxs = ["review_state", ])
        if not "retract all analyses" in ws.REQUEST['workflow_skiplist']:
            # retract all analyses in this WS.
            # (NB: don't retract if it's verified)
            analyses = ws.getAnalyses()
            for analysis in analyses:
                if wf.getInfoFor(analysis, 'review_state', '') not in ('attachment_due', 'to_be_verified',) or \
                   wf.getInfoFor(analysis, 'cancellation_state', '') != 'active':
                    continue
                if not analysis.UID in ws.REQUEST['workflow_skiplist']:
                    wf.doActionFor(analysis, 'retract')

    elif event.action == "verify":
        ws.reindexObject(idxs = ["review_state", ])
        if not "verify all analyses" in ws.REQUEST['workflow_skiplist']:
            # verify all analyses in this WS.
            analyses = ws.getAnalyses()
            for analysis in analyses:
                if wf.getInfoFor(analysis, 'review_state', '') != 'to_be_verified' or \
                   wf.getInfoFor(analysis, 'cancellation_state', '') != 'active':
                    continue
                if not analysis.UID in ws.REQUEST['workflow_skiplist']:
                    wf.doActionFor(analysis, "verify")

    return
