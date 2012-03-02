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
            logger.info("part Skip")
            return
        else:
            part.REQUEST["workflow_skiplist"].append(part.UID())

    logger.info("Starting: %s on %s" % (event.transition.id, part))

    workflow = getToolByName(part, 'portal_workflow')
    sample = part.aq_parent
    sample_state = workflow.getInfoFor(sample, 'review_state')

    if event.transition.id == "receive":
        if sample.getDateSampled() > DateTime():
            raise WorkflowException
        part.setDateReceived(DateTime())
        part.reindexObject(idxs = ["getDateReceived", ])

        # if all sibling partitions are received, promote sample
        if not sample.UID() in part.REQUEST['workflow_skiplist']:
            due = [sp for sp in sample.objectValues("SamplePartition")
                   if workflow.getInfoFor(sp, 'review_state') == 'due']
            if sample_state == 'due' and not due:
                workflow.doActionFor(sample, 'receive')


    elif event.transition.id == "expire":
        part.setDateExpired(DateTime())
        part.reindexObject(idxs = ["review_state", "getDateExpired", ])


    #---------------------
    # Secondary workflows:
    #---------------------

    elif event.transition.id == "reinstate":
        part.reindexObject(idxs = ["cancellation_state", ])

        # Re-instate all sample partitions
        for sp in [sp for sp in parts
                   if workflow.getInfoFor(sp, 'cancellation_state') == 'cancelled']:
            workflow.doActionFor(sp, 'reinstate')

    elif event.transition.id == "cancel":
        sample.reindexObject(idxs = ["cancellation_state", ])

        # Re-instate all sample partitions
        for sp in [sp for sp in parts
                   if workflow.getInfoFor(sp, 'cancellation_state') == 'cancelled']:
            workflow.doActionFor(sp, 'reinstate')

    return
