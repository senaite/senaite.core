from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
import transaction

def AfterTransitionEventHandler(instance, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    action_id = event.transition.id

    if skip(instance, action_id):
        return

    workflow = getToolByName(instance, 'portal_workflow')

    if action_id == "attach":
        instance.reindexObject(idxs = ["review_state", ])
        # Don't cascade. Shouldn't be attaching ARs for now (if ever).
        return

    elif action_id == "sample":
        # transition our sample
        sample = instance.getSample()
        if not skip(sample, action_id, peek=True):
            workflow.doActionFor(sample, action_id)

    elif action_id == "to_be_preserved":
        pass

    elif action_id == "sample_due":
        pass

    elif action_id == "preserve":
        # transition our sample
        sample = instance.getSample()
        if not skip(sample, action_id, peek=True):
            workflow.doActionFor(sample, action_id)

    elif action_id == "receive":
        instance.setDateReceived(DateTime())
        instance.reindexObject(idxs = ["review_state", "getDateReceived", ])

        # receive the AR's sample
        sample = instance.getSample()
        if not skip(sample, action_id, peek=True):
            # unless this is a secondary AR
            if workflow.getInfoFor(sample, 'review_state') == 'sample_due':
                workflow.doActionFor(sample, 'receive')

        # receive all analyses in this AR.
        analyses = instance.getAnalyses(review_state = 'sample_due')
        for analysis in analyses:
            if not skip(analysis, action_id):
                workflow.doActionFor(analysis.getObject(), 'receive')

    elif action_id == "submit":
        instance.reindexObject(idxs = ["review_state", ])
        # Don't cascade. Shouldn't be submitting ARs directly for now.

    elif action_id == "retract":
        instance.reindexObject(idxs = ["review_state", ])
        if not "retract all analyses" in instance.REQUEST['workflow_skiplist']:
            # retract all analyses in this AR.
            # (NB: don't retract if it's verified)
            analyses = instance.getAnalyses(review_state = ('attachment_due', 'to_be_verified',))
            for analysis in analyses:
                doActionFor(analysis.getObject(), 'retract')

    elif action_id == "verify":
        instance.reindexObject(idxs = ["review_state", ])
        if not "verify all analyses" in instance.REQUEST['workflow_skiplist']:
            # verify all analyses in this AR.
            analyses = instance.getAnalyses(review_state = 'to_be_verified')
            for analysis in analyses:
                doActionFor(analysis.getObject(), "verify")

    elif action_id == "publish":
        instance.reindexObject(idxs = ["review_state", "getDatePublished", ])
        if not "publish all analyses" in instance.REQUEST['workflow_skiplist']:
            # publish all analyses in this AR. (except not requested ones)
            analyses = instance.getAnalyses(review_state = 'verified')
            for analysis in analyses:
                doActionFor(analysis.getObject(), "publish")

    #---------------------
    # Secondary workflows:
    #---------------------

    elif action_id == "reinstate":
        instance.reindexObject(idxs = ["cancellation_state", ])
        # activate all analyses in this AR.
        analyses = instance.getAnalyses(cancellation_state = 'cancelled')
        for analysis in analyses:
            doActionFor(analysis.getObject(), 'reinstate')

    elif action_id == "cancel":
        instance.reindexObject(idxs = ["cancellation_state", ])
        # deactivate all analyses in this AR.
        analyses = instance.getAnalyses(cancellation_state = 'active')
        for analysis in analyses:
            doActionFor(analysis.getObject(), 'cancel')

    return
