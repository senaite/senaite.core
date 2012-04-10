from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import App
import transaction

def AfterTransitionEventHandler(instance, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    debug_mode = App.config.getConfiguration().debug_mode
    if not debug_mode:
        return

    skiplist = instance.REQUEST.get('workflow_skiplist', [])

    if instance.UID() in skiplist:
        logger.info("Ignored transition %s on %s" %
                    (event.transition.id, instance))
    else:
        logger.info("Started transition %s on %s" %
                    (event.transition.id, instance))
