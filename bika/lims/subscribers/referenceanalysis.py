from AccessControl import getSecurityManager
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import transaction

def AfterTransitionEventHandler(analysis, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    if event.transition.id == "verify":
        analysis.setDateVerified(DateTime())
