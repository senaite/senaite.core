from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims import logger

def ActionSucceededEventHandler(sample, event):

    if not sample.REQUEST.has_key('workflow_skiplist'):
        sample.REQUEST['workflow_skiplist'] = [sample.UID(), ]
        skiplist = sample.REQUEST['workflow_skiplist']
    else:
        skiplist = sample.REQUEST['workflow_skiplist']
        if sample.UID() in skiplist:
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
            if not ar.UID() in skiplist:
                workflow.doActionFor(ar, "receive")

    elif event.action == "expire":
        sample.setDateExpired(DateTime())
        sample.reindexObject(idxs = ["review_state", "getDateExpired", ])

    logger.info("Finished with: %s on %s" % (event.action, sample))
