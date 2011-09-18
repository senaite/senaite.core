from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ActionSucceededEventHandler(ar, event):

    if event.action == "attach":
        # Need a separate skiplist for this due to double-jumps with 'submit'.
        if not ar.REQUEST.has_key('workflow_attach_skiplist'):
            ar.REQUEST['workflow_attach_skiplist'] = [ar.UID(), ]
        else:
            if ar.UID() in ar.REQUEST['workflow_attach_skiplist']:
                logger.info("AR Skip")
                return
            else:
                ar.REQUEST["workflow_attach_skiplist"].append(ar.UID())

        logger.info("Starting: %s on %s" % (event.action, ar))

        ar.reindexObject(idxs = ["review_state", ])
        # Don't cascade. Shouldn't be attaching ARs for now (if ever).
        return

    if not ar.REQUEST.has_key('workflow_skiplist'):
        ar.REQUEST['workflow_skiplist'] = [ar.UID(), ]
        skiplist = ar.REQUEST['workflow_skiplist']
    else:
        skiplist = ar.REQUEST['workflow_skiplist']
        if ar.UID() in skiplist:
            logger.info("AR Skip")
            return
        else:
            ar.REQUEST["workflow_skiplist"].append(ar.UID())

    logger.info("Starting: %s on %s" % (event.action, ar))

    wf = getToolByName(ar, 'portal_workflow')

    if event.action == "receive":
        ar.setDateReceived(DateTime())
        ar.reindexObject(idxs = ["review_state", "getDateReceived", ])

        # receive the AR's sample
        sample = ar.getSample()
        if not sample.UID() in skiplist:
            wf.doActionFor(sample, 'receive')

        # receive all analyses in this AR.
        analyses = ar.getAnalyses(review_state = 'sample_due')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                wf.doActionFor(analysis.getObject(), 'receive')

    elif event.action == "submit":
        ar.reindexObject(idxs = ["review_state", ])
        # Don't cascade. Shouldn't be submitting ARs for now.

    elif event.action == "retract":
        ar.reindexObject(idxs = ["review_state", ])
        if not "retract all analyses" in skiplist:
            # retract all analyses in this AR.
            # (NB: don't retract if it's published)
            analyses = ar.getAnalyses(review_state = ('attachment_due', 'to_be_verified', 'verified',))
            for analysis in analyses:
                if not analysis.UID in skiplist:
                    wf.doActionFor(analysis.getObject(), 'retract')

    elif event.action == "verify":
        ar.reindexObject(idxs = ["review_state", ])
        # verify all analyses in this AR.
        analyses = ar.getAnalyses(review_state = 'to_be_verified')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                wf.doActionFor(analysis.getObject(), "verify")

    elif event.action == "publish":
        ar.setDatePublished(DateTime())
        ar.reindexObject(idxs = ["review_state", "getDatePublished", ])
        # publish all analyses in this AR. (except not requested ones)
        analyses = ar.getAnalyses(review_state = 'verified')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                wf.doActionFor(analysis.getObject(), "publish")

    #---------------------
    # Secondary workflows:
    #---------------------

    elif event.action == "activate":
        ar.reindexObject(idxs = ["inactive_review_state", ])
        # activate all analyses in this AR.
        analyses = ar.getAnalyses(inactive_review_state = 'inactive')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                wf.doActionFor(analysis.getObject(), 'activate')

    elif event.action == "deactivate":
        ar.reindexObject(idxs = ["inactive_review_state", ])
        # deactivate all analyses in this AR.
        analyses = ar.getAnalyses(inactive_review_state = 'active')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                wf.doActionFor(analysis.getObject(), 'deactivate')

    return
