from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName

def ActionSucceededEventHandler(sample, event):
    workflow = getToolByName(sample, 'portal_workflow')
    pc = getToolByName(sample, 'portal_catalog')
    rc = getToolByName(sample, 'reference_catalog')

    # set this before transitioning to prevent this handler from reacting
    if hasattr(sample, '_skip_ActionSucceededEvent'):
        del sample._skip_ActionSucceededEvent
        return

    elif event.action == "receive":
        # when a sample is received, all associated
        # AnalysisRequests are also transitioned
        sample.setDateReceived(DateTime())
        sample.reindexObject()
        for ar in sample.getAnalysisRequests():
            review_state = workflow.getInfoFor(ar, 'review_state')
            if review_state == 'sample_due':
                sample._skip_ActionSucceededEvent = 1
                workflow.doActionFor(ar, event.action)
                ar.reindexObject()
