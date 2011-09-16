from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims import logger

def ActionSucceededEventHandler(sample, event):

    logger.info("Succeeded: %s on %s" % (event.action, sample))

    skiplist = sample.REQUEST["workflow_skiplist"]
    skiplist.append(sample.UID())

    if event.action == "receive":
        sample.setDateReceived(DateTime())
        sample.reindexObject(idxs = ["getDateReceived", ])
        # when a sample is received, all associated
        # AnalysisRequests are also transitioned
        workflow = getToolByName(sample, 'portal_workflow')
        for ar in sample.getAnalysisRequests():
            if not ar.UID() in skiplist:
                workflow.doActionFor(ar, "receive")

    elif event.action == "expire":
        sample.setDateExpired(DateTime())
        sample.reindexObject(idxs = ["getDateExpired", ])
