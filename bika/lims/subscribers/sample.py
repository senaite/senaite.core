from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims.subscribers import skip
from bika.lims.subscribers import doActionFor
from bika.lims import logger

def AfterTransitionEventHandler(instance, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    action_id = event.transition.id

    if skip(instance, action_id):
        return

    workflow = getToolByName(instance, 'portal_workflow')
    membership_tool = getToolByName(instance, 'portal_membership')
    member = membership_tool.getAuthenticatedMember()
    parts = instance.objectValues('SamplePartition')

    if action_id == "sample":
        # This action can happen in the Sample UI.  So we transition all
        # instance partitions that are still 'to_be_sampled'
        tbs = [sp for sp in parts
               if workflow.getInfoFor(sp, 'review_state') == 'to_be_sampled']
        for sp in tbs:
            doActionFor(sp, action_id)
        # All associated AnalysisRequests are also transitioned
        for ar in instance.getAnalysisRequests():
            doActionFor(ar, action_id)
            ar.reindexObject()

    elif action_id == "to_be_preserved":
        # Transition our children
        tbs = [sp for sp in parts
               if workflow.getInfoFor(sp, 'review_state') == 'to_be_preserved']
        for sp in tbs:
            doActionFor(sp, action_id)
        # All associated AnalysisRequests are also transitioned
        for ar in instance.getAnalysisRequests():
            doActionFor(ar, action_id)
            ar.reindexObject()

    elif action_id == "sample_due":
        # All associated AnalysisRequests are also transitioned
        for ar in instance.getAnalysisRequests():
            doActionFor(ar, action_id)
            ar.reindexObject()

    elif action_id == "preserve":
        # This action can happen in the Sample UI.  So we transition all
        # instance partitions that are still 'to_be_preserved'
        tbs = [sp for sp in parts
               if workflow.getInfoFor(sp, 'review_state') == 'to_be_preserved']
        for sp in tbs:
            doActionFor(sp, action_id)
        # All associated AnalysisRequests are also transitioned
        for ar in instance.getAnalysisRequests():
            doActionFor(ar, action_id)
            ar.reindexObject()

    elif action_id == "receive":

        instance.setDateReceived(DateTime())
        instance.reindexObject(idxs = ["review_state", "getDateReceived"])

        # Receive all instance partitions that are still 'sample_due'
        sample_due = [sp for sp in parts
                      if workflow.getInfoFor(sp, 'review_state') == 'sample_due']
        for sp in sample_due:
            workflow.doActionFor(sp, 'receive')

        # when a instance is received, all associated
        # AnalysisRequests are also transitioned
        for ar in instance.getAnalysisRequests():
            doActionFor(ar, "receive")

    elif action_id == "expire":
        instance.setDateExpired(DateTime())
        instance.reindexObject(idxs = ["review_state", "getDateExpired", ])

    #---------------------
    # Secondary workflows:
    #---------------------

    elif action_id == "reinstate":
        instance.reindexObject(idxs = ["cancellation_state", ])

        # Re-instate all instance partitions
        for sp in [sp for sp in parts
                   if workflow.getInfoFor(sp, 'cancellation_state') == 'cancelled']:
            workflow.doActionFor(sp, 'reinstate')

        # reinstate all ARs for this instance.
        ars = instance.getAnalysisRequests()
        for ar in ars:
            if not skip(ar, action_id, peek=True):
                ar_state = workflow.getInfoFor(ar, 'cancellation_state')
                if ar_state == 'cancelled':
                    workflow.doActionFor(ar, 'reinstate')

    elif action_id == "cancel":
        instance.reindexObject(idxs = ["cancellation_state", ])

        # Cancel all partitions
        for sp in [sp for sp in parts
                   if workflow.getInfoFor(sp, 'cancellation_state') == 'active']:
            workflow.doActionFor(sp, 'cancel')

        # cancel all ARs for this instance.
        ars = instance.getAnalysisRequests()
        for ar in ars:
            if not skip(ar, action_id, peek=True):
                ar_state = workflow.getInfoFor(ar, 'cancellation_state')
                if ar_state == 'active':
                    workflow.doActionFor(ar, 'cancel')

    return
