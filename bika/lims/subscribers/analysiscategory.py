from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
import transaction

def AfterTransitionEventHandler(instance, event):

    wf = getToolByName(instance, 'portal_workflow')
    rc = getToolByName(instance, REFERENCE_CATALOG)
    pu = getToolByName(instance, 'plone_utils')

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    if event.transition.id == "deactivate":
        # A instance cannot be deactivated if it contains services
        bsc = getToolByName(instance, 'bika_setup_catalog')
        ars = bsc(portal_type='AnalysisService', getCategoryUID = instance.UID())
        if ars:
            message = _("Category cannot be deactivated because it contains Analysis Services")
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException
