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
    else:
        skiplist = ar.REQUEST['workflow_skiplist']
        if ar.UID() in skiplist:
        # Special case: when an analysis is added, it retracts the AR,
        # but we don't want that action to cascade.
            return
        else:
            ar.REQUEST["workflow_skiplist"].append(ar.UID())

    logger.info("Succeeded: %s on %s" % (event.action, ar))

    wf = getToolByName(ar, 'portal_workflow')

    if event.action == "receive":
        ar.setDateReceived(DateTime())
        ar.reindexObject(idxs = ["getDateReceived", ])

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
        # Submit analyses
        analyses = ar.getAnalyses(review_state = 'sample_received')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                wf.doActionFor(analysis.getObject(), "submit")

    elif event.action == "retract":
        # retract all analyses in this AR.
        analyses = ar.getAnalyses(review_state = ('to_be_verified', 'verified',))
        for analysis in analyses:
            if not analysis.UID in skiplist:
                if analysis.review_state != 'sample_received':
                    wf.doActionFor(analysis.getObject(), 'retract')

    elif event.action == "verify":
        # verify all analyses in this AR.
        analyses = ar.getAnalyses(review_state = 'to_be_verified')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                wf.doActionFor(analysis.getObject(), "verify")

    elif event.action == "publish":
        ar.setDatePublished(DateTime())
        ar.reindexObject(idxs = ["getDatePublished", ])
        # publish all analyses in this AR.
        analyses = ar.getAnalyses(review_state = 'verified')
        for analysis in analyses:
            if not analysis.UID in skiplist:
                wf.doActionFor(analysis.getObject(), "publish")







