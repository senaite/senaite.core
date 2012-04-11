from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.subscribers import skip
from bika.lims.subscribers import doActionFor
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
        # Don't cascade. Shouldn't be attaching WSs for now (if ever).
        return

    elif action_id == "submit":
        # Don't cascade. Shouldn't be submitting WSs directly for now,
        # except edge cases where all analyses are already submitted,
        # but instance was held back until an analyst was assigned.
        instance.reindexObject(idxs = ["review_state", ])
        can_attach = True
        for a in instance.getAnalyses():
            if workflow.getInfoFor(a, 'review_state') in \
               ('to_be_sampled', 'to_be_preserved', 'sample_due',
                'sample_received', 'attachment_due', 'assigned',):
                # Note: referenceanalyses and duplicateanalyses can still have review_state = "assigned".
                can_attach = False
                break
        if can_attach:
            doActionFor(instance, 'attach')

    elif action_id == "retract":
        instance.reindexObject(idxs = ["review_state", ])
        if not "retract all analyses" in instance.REQUEST['workflow_skiplist']:
            # retract all analyses in this instance.
            # (NB: don't retract if it's verified)
            analyses = instance.getAnalyses()
            for analysis in analyses:
                if workflow.getInfoFor(analysis, 'review_state', '') not in ('attachment_due', 'to_be_verified',):
                    continue
                doActionFor(analysis, 'retract')

    elif action_id == "verify":
        instance.reindexObject(idxs = ["review_state", ])
        if not "verify all analyses" in instance.REQUEST['workflow_skiplist']:
            # verify all analyses in this instance.
            analyses = instance.getAnalyses()
            for analysis in analyses:
                if workflow.getInfoFor(analysis, 'review_state', '') != 'to_be_verified':
                    continue
                doActionFor(analysis, "verify")

    return
