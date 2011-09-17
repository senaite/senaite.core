from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def ActionSucceededEventHandler(ar, event):

    if not ar.REQUEST.has_key('workflow_skiplist'):
        ar.REQUEST['workflow_skiplist'] = [ar.UID(), ]
        skiplist = ar.REQUEST['workflow_skiplist']
    else:
        skiplist = ar.REQUEST['workflow_skiplist']
        if ar.UID() in skiplist:
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
        # Submit analyses
        analyses = ar.getAnalyses(review_state = 'sample_received')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                a = analysis.getObject()
                if a.getResult():
                    wf.doActionFor(a, "submit")

    elif event.action == "retract":
        ar.reindexObject(idxs = ["review_state", ])
        if not "retract all analyses" in skiplist:
            # retract all analyses in this AR.
            analyses = ar.getAnalyses(review_state = ('to_be_verified', 'verified',))
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

    logger.info("Finished with: %s on %s" % (event.action, ar))
