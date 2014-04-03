from AccessControl import getSecurityManager
from Acquisition import aq_inner
from bika.lims import logger
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import changeWorkflowState
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
import transaction
import zope.event


def ARImportModifiedEventHandler(instance, event):

    if instance.portal_type != "ARImport":
        print 'How does this happen'
        return

    instance.validateIt()

def ARImportItemModifiedEventHandler(instance, event):

    if instance.portal_type != "ARImportItem":
        print 'How does this happen'
        return

    instance.aq_inner.aq_parent.validateIt()
