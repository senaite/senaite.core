from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims import logger

def ActionSucceededEventHandler(sample, event):

    if not sample.REQUEST.has_key('workflow_skiplist'):
        sample.REQUEST['workflow_skiplist'] = [sample.UID(), ]
    else:
        if sample.UID() in sample.REQUEST['workflow_skiplist']:
            logger.info("SM Skip")
            return
        else:
            sample.REQUEST["workflow_skiplist"].append(sample.UID())

    logger.info("Starting: %s on %s" % (event.action, sample))

    workflow = getToolByName(sample, 'portal_workflow')

    if event.action == "receive":
        sample.setDateReceived(DateTime())
        sample.reindexObject(idxs = ["review_state", "getDateReceived", ])
        # when a sample is received, all associated
        # AnalysisRequests are also transitioned
        for ar in sample.getAnalysisRequests():
            if not ar.UID() in sample.REQUEST['workflow_skiplist']:
                workflow.doActionFor(ar, "receive")

    elif event.action == "expire":
        sample.setDateExpired(DateTime())
        sample.reindexObject(idxs = ["review_state", "getDateExpired", ])

    #---------------------
    # Secondary workflows:
    #---------------------

    elif event.action == "reinstate":
        sample.reindexObject(idxs = ["cancellation_review_state", ])
        # reinstate all ARs for this sample.
        ars = sample.getAnalysisRequests()
        for ar in ars:
            if not ar.UID in sample.REQUEST['workflow_skiplist']:
                ar_state = workflow.getInfoFor(ar, 'cancellation_review_state')
                if ar_state == 'cancelled':
                    workflow.doActionFor(ar, 'reinstate')

    elif event.action == "cancel":
        sample.reindexObject(idxs = ["cancellation_review_state", ])
        # cancel all ARs for this sample.
        ars = sample.getAnalysisRequests()
        for ar in ars:
            if not ar.UID in sample.REQUEST['workflow_skiplist']:
                ar_state = workflow.getInfoFor(ar, 'cancellation_review_state')
                if ar_state == 'active':
                    workflow.doActionFor(ar, 'cancel')

    return
