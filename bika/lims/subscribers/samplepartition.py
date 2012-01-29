from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims import logger

def AfterTransitionEventHandler(spart, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    if not spart.REQUEST.has_key('workflow_skiplist'):
        spart.REQUEST['workflow_skiplist'] = [spart.UID(), ]
    else:
        if spart.UID() in spart.REQUEST['workflow_skiplist']:
            logger.info("SPART Skip")
            return
        else:
            spart.REQUEST["workflow_skiplist"].append(spart.UID())

    logger.info("Starting: %s on %s" % (event.transition.id, spart))

    workflow = getToolByName(spart, 'portal_workflow')

    if event.transition.id == "expire":
        spart.setDateExpired(DateTime())
        spart.reindexObject(idxs = ["review_state", "getDateExpired", ])

    return
