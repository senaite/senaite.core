from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName

def ActionSucceededEventHandler(sample, event):

    if hasattr(sample, '_skip_ActionSucceededEventHandler'):
        return

    workflow = getToolByName(sample, 'portal_workflow')
    pc = getToolByName(sample, 'portal_catalog')
    rc = getToolByName(sample, 'reference_catalog')

    if event.action == "receive":
        # when a sample is received, all associated
        # AnalysisRequests are also transitioned
        sample.setDateReceived(DateTime())
        sample.reindexObject()
        for ar in sample.getAnalysisRequests():
            try:
                workflow.doActionFor(ar, 'receive')
            except:
                pass

    elif event.action == "expire":
        sample.setDateExpired(DateTime())
        sample.reindexObject()
