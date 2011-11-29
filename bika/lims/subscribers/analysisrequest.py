from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def AfterTransitionEventHandler(ar, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    if event.transition.id == "attach":
        # Need a separate skiplist for this due to double-jumps with 'submit'.
        if not ar.REQUEST.has_key('workflow_attach_skiplist'):
            ar.REQUEST['workflow_attach_skiplist'] = [ar.UID(), ]
        else:
            if ar.UID() in ar.REQUEST['workflow_attach_skiplist']:
                logger.info("AR Skip")
                return
            else:
                ar.REQUEST["workflow_attach_skiplist"].append(ar.UID())

        logger.info("Starting: %s on %s" % (event.transition.id, ar))

        ar.reindexObject(idxs = ["review_state", ])
        # Don't cascade. Shouldn't be attaching ARs for now (if ever).
        return

    if not ar.REQUEST.has_key('workflow_skiplist'):
        ar.REQUEST['workflow_skiplist'] = [ar.UID(), ]
    else:
        if ar.UID() in ar.REQUEST['workflow_skiplist']:
            logger.info("AR Skip")
            return
        else:
            ar.REQUEST["workflow_skiplist"].append(ar.UID())

    logger.info("Starting: %s on %s" % (event.transition.id, ar))

    wf = getToolByName(ar, 'portal_workflow')

    if event.transition.id == "receive":
        ar.setDateReceived(DateTime())
        ar.reindexObject(idxs = ["review_state", "getDateReceived", ])

        # receive the AR's sample
        sample = ar.getSample()
        if sample.UID() not in ar.REQUEST['workflow_skiplist']:
            # unless this is a secondary AR
            if wf.getInfoFor(sample, 'review_state') == 'due':
                wf.doActionFor(sample, 'receive')

        # receive all analyses in this AR.
        analyses = ar.getAnalyses(review_state = 'sample_due')
        for analysis in analyses:
            if not analysis.UID in ar.REQUEST['workflow_skiplist']:
                wf.doActionFor(analysis.getObject(), 'receive')

    elif event.transition.id == "submit":
        ar.reindexObject(idxs = ["review_state", ])
        # Don't cascade. Shouldn't be submitting ARs directly for now.

    elif event.transition.id == "retract":
        ar.reindexObject(idxs = ["review_state", ])
        if not "retract all analyses" in ar.REQUEST['workflow_skiplist']:
            # retract all analyses in this AR.
            # (NB: don't retract if it's verified)
            analyses = ar.getAnalyses(review_state = ('attachment_due', 'to_be_verified',))
            for analysis in analyses:
                if not analysis.UID in ar.REQUEST['workflow_skiplist']:
                    wf.doActionFor(analysis.getObject(), 'retract')

    elif event.transition.id == "verify":
        ar.reindexObject(idxs = ["review_state", ])
        if not "verify all analyses" in ar.REQUEST['workflow_skiplist']:
            # verify all analyses in this AR.
            analyses = ar.getAnalyses(review_state = 'to_be_verified')
            for analysis in analyses:
                if not analysis.UID in ar.REQUEST['workflow_skiplist']:
                    wf.doActionFor(analysis.getObject(), "verify")

    elif event.transition.id == "publish":
        ar.reindexObject(idxs = ["review_state", "getDatePublished", ])
        if not "publish all analyses" in ar.REQUEST['workflow_skiplist']:
            # publish all analyses in this AR. (except not requested ones)
            analyses = ar.getAnalyses(review_state = 'verified')
            for analysis in analyses:
                if not analysis.UID in ar.REQUEST['workflow_skiplist']:
                    wf.doActionFor(analysis.getObject(), "publish")

    #---------------------
    # Secondary workflows:
    #---------------------

    elif event.transition.id == "reinstate":
        ar.reindexObject(idxs = ["cancellation_state", ])
        # activate all analyses in this AR.
        analyses = ar.getAnalyses(cancellation_state = 'cancelled')
        for analysis in analyses:
            if not analysis.UID in ar.REQUEST['workflow_skiplist']:
                wf.doActionFor(analysis.getObject(), 'reinstate')

    elif event.transition.id == "cancel":
        ar.reindexObject(idxs = ["cancellation_state", ])
        # deactivate all analyses in this AR.
        analyses = ar.getAnalyses(cancellation_state = 'active')
        for analysis in analyses:
            if not analysis.UID in ar.REQUEST['workflow_skiplist']:
                wf.doActionFor(analysis.getObject(), 'cancel')

    return
