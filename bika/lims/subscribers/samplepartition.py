from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims import logger

def AfterTransitionEventHandler(part, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    if not part.REQUEST.has_key('workflow_skiplist'):
        part.REQUEST['workflow_skiplist'] = [part.UID(), ]
    else:
        if part.UID() in part.REQUEST['workflow_skiplist']:
            ##logger.info("part Skip")
            return
        else:
            part.REQUEST["workflow_skiplist"].append(part.UID())

    logger.info("Starting: %s on %s" % (event.transition.id, part))

    workflow = getToolByName(part, 'portal_workflow')
    membership_tool = getToolByName(part, 'portal_membership')
    member = membership_tool.getAuthenticatedMember()
    sample = part.aq_parent
    sample_state = workflow.getInfoFor(sample, 'review_state')

    if event.transition.id == "sampled":

        # set "Sampled" on all our Analyses
        analyses = part.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            workflow.doActionFor(analysis, 'sampled')

        # This transition is only called from sample.py in the "sampled"
        # handler - so we let the sample take care of itself

    elif event.transition.id == "preserved":

        # set "Preserved" on all our Analyses
        analyses = part.getBackReferences('AnalysisSamplePartition')
        for analysis in analyses:
            workflow.doActionFor(analysis, 'preserved')

        # This transition is called directly on the SamplePartition object,
        # so we promote the sample.
        try:
            workflow.doActionFor(sample, 'preserved')
        except WorkflowException:
            # guard_preserved_transition may fail if the states
            # of our sibling partitions prevent sample transition
            pass

    elif event.transition.id == "receive":
        if sample.getSamplingDate() > DateTime():
            raise WorkflowException
        part.setDateReceived(DateTime())
        part.reindexObject(idxs = ["getDateReceived", ])

        # if all sibling partitions are received, promote sample
        if not sample.UID() in part.REQUEST['workflow_skiplist']:
            sample_due = [sp for sp in sample.objectValues("SamplePartition")
                          if workflow.getInfoFor(sp, 'review_state') == 'sample_due']
            if sample_state == 'sample_due' and not sample_due:
                workflow.doActionFor(sample, 'receive')


    elif event.transition.id == "expire":
        part.setDateExpired(DateTime())
        part.reindexObject(idxs = ["review_state", "getDateExpired", ])


    #---------------------
    # Secondary workflows:
    #---------------------

    elif event.transition.id == "reinstate":
        part.reindexObject(idxs = ["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')

        # if all sibling partitions are active, activate sample
        if not sample.UID() in part.REQUEST['workflow_skiplist']:
            cancelled = [sp for sp in sample.objectValues("SamplePartition")
                         if workflow.getInfoFor(sp, 'cancellation_state') == 'cancelled']
            if sample_c_state == 'cancelled' and not cancelled:
                workflow.doActionFor(sample, 'reinstate')

    elif event.transition.id == "cancel":
        part.reindexObject(idxs = ["cancellation_state", ])
        sample_c_state = workflow.getInfoFor(sample, 'cancellation_state')

        # if all sibling partitions are cancelled, cancel sample
        if not sample.UID() in part.REQUEST['workflow_skiplist']:
            active = [sp for sp in sample.objectValues("SamplePartition")
                      if workflow.getInfoFor(sp, 'cancellation_state') == 'active']
            if sample_c_state == 'active' and not active:
                workflow.doActionFor(sample, 'cancel')

    return
