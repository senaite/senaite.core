from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims import logger
from bika.lims.subscribers import skip
from bika.lims.subscribers import doActionFor
import App
import transaction

def AfterTransitionEventHandler(instance, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    debug_mode = App.config.getConfiguration().debug_mode
    if not debug_mode:
        return

    if not skip(instance, event.transition.id, peek=True):
        logger.debug("Started transition %s on %s" %
                    (event.transition.id, instance))
##    else:
##        logger.info("Ignored transition %s on %s" %
##                    (event.transition.id, instance))
