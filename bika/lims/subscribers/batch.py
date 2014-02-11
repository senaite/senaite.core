from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims.subscribers import skip
from bika.lims.subscribers import doActionFor


def BeforeTransitionEventHandler(instance, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    action_id = event.transition.id

    if skip(instance, action_id):
        return

    wf = getToolByName(instance, 'portal_workflow')

    if action_id == "cancel":
        # Before cancelling the AR we transition to 'cancelled' state all
        # contained ARs
        for ar in instance.getAnalysisRequests():
            if wf.getInfoFor(ar, 'cancellation_state') != 'active':
                doActionFor(ar, 'cancel')
                ar.reindexObject()
