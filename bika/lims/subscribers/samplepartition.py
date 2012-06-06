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
    sample = instance.aq_parent
    sample_state = workflow.getInfoFor(sample, 'review_state')

    if action_id == "sample":
        # Transition our analyses
        analyses = instance.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            doActionFor(analysis, action_id)
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_sampled',]
            escalate = True
            for part in parts:
                pstate = workflow.getInfoFor(part, 'review_state')
                if pstate in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, action_id)
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, action_id)

    elif action_id == "to_be_preserved":
        # Transition our analyses
        analyses = instance.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            doActionFor(analysis, action_id)
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_sampled', 'to_be_preserved',]
            escalate = True
            for part in parts:
                if workflow.getInfoFor(part, 'review_state') in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, action_id)
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, action_id)

    elif action_id == "sample_due":
        # Transition our analyses
        analyses = instance.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            doActionFor(analysis, action_id)
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_preserved',]
            escalate = True
            for part in parts:
                pstate =  workflow.getInfoFor(part, 'review_state')
                if pstate in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, action_id)
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, action_id)

    elif action_id == "preserve":
        # Transition our analyses
        analyses = instance.getBackReferences('AnalysisSamplePartition')
        if analyses:
            for analysis in analyses:
                doActionFor(analysis, action_id)
        # if all our siblings are now up to date, promote sample and ARs.
        parts = sample.objectValues("SamplePartition")
        if parts:
            lower_states = ['to_be_sampled', 'to_be_preserved', ]
            escalate = True
            for part in parts:
                if workflow.getInfoFor(part, 'review_state') in lower_states:
                    escalate = False
            if escalate:
                doActionFor(sample, action_id)
                for ar in sample.getAnalysisRequests():
                    doActionFor(ar, action_id)

    elif action_id == "receive":
        if sample.getSamplingDate() > DateTime():
            raise WorkflowException
        instance.setDateReceived(DateTime())
        instance.reindexObject(idxs = ["getDateReceived", ])
        # Transition our analyses
        analyses = instance.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            doActionFor(analysis, action_id)
        # if all sibling partitions are received, promote sample
        if not skip(sample, action_id, peek=True):
            due = [sp for sp in sample.objectValues("SamplePartition")
                   if workflow.getInfoFor(sp, 'review_state') == 'sample_due']
            if sample_state == 'sample_due' and not due:
                doActionFor(sample, 'receive')

    elif action_id == "expire":
        instance.setDateExpired(DateTime())
        instance.reindexObject(idxs = ["review_state", "getDateExpired", ])

    #---------------------
    # Secondary workflows:
    #---------------------

    elif action_id == "reinstate":
        instance.reindexObject(idxs = ["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')

        # if all sibling partitions are active, activate sample
        if not skip(sample, action_id, peek=True):
            cancelled = [sp for sp in sample.objectValues("SamplePartition")
                         if workflow.getInfoFor(sp, 'cancellation_state') == 'cancelled']
            if sample_c_state == 'cancelled' and not cancelled:
                workflow.doActionFor(sample, 'reinstate')

    elif action_id == "cancel":
        instance.reindexObject(idxs = ["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')

        # if all sibling partitions are cancelled, cancel sample
        if not skip(sample, action_id, peek=True):
            active = [sp for sp in sample.objectValues("SamplePartition")
                      if workflow.getInfoFor(sp, 'cancellation_state') == 'active']
            if sample_c_state == 'active' and not active:
                workflow.doActionFor(sample, 'cancel')

    return
