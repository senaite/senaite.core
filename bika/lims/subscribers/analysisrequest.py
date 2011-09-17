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
            logger.info("%s says: Oh, FFS, not %s again!!" % (ar, event.action))
            return
        else:
            ar.REQUEST["workflow_skiplist"].append(ar.UID())

    logger.info("Processing: %s on %s" % (event.action, ar))

    wf = getToolByName(ar, 'portal_workflow')

    if event.action == "receive":
        ar.setDateReceived(DateTime())
        ar.reindexObject(idxs = ["review_state", "getDateReceived", ])

        # receive the AR's sample
        sample = ar.getSample()
        if not sample.UID() in skiplist:
            logger.info("%s involking: %s on %s" % (ar, event.action, sample))
            wf.doActionFor(sample, 'receive')

        # receive all analyses in this AR.
        analyses = ar.getAnalyses(review_state = 'sample_due')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                logger.info("%s involking: %s on %s" % (ar, event.action, analysis.getObject().getService().getKeyword()))
                wf.doActionFor(analysis.getObject(), 'receive')

    elif event.action == "submit":
        ar.reindexObject(idxs = ["review_state", ])
        # Submit analyses
        analyses = ar.getAnalyses(review_state = 'sample_received')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                a = analysis.getObject()
                if a.getResult():
                    logger.info("%s involking: %s on %s" % (ar, event.action, a.getService().getKeyword()))
                    wf.doActionFor(a, "submit")

    elif event.action == "retract":
        ar.reindexObject(idxs = ["review_state", ])
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

    logger.info("Finished with: %s on %s" % (event.action, ar))






