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

    if event.action == "receive":
        sample.setDateReceived(DateTime())
        sample.reindexObject(idxs = ["review_state", "getDateReceived", ])
        # when a sample is received, all associated
        # AnalysisRequests are also transitioned
        workflow = getToolByName(sample, 'portal_workflow')
        for ar in sample.getAnalysisRequests():
            if not ar.UID() in sample.REQUEST['workflow_skiplist']:
                workflow.doActionFor(ar, "receive")

    elif event.action == "expire":
        sample.setDateExpired(DateTime())
        sample.reindexObject(idxs = ["review_state", "getDateExpired", ])

    return
