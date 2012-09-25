from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
import transaction

def AfterTransitionEventHandler(instance, event):

    # creation doesn't have a 'transition'
    if not event.transition:
        return

    wf = getToolByName(instance, 'portal_workflow')
    bsc = getToolByName(instance, 'bika_setup_catalog')
    rc = getToolByName(instance, REFERENCE_CATALOG)
    pu = getToolByName(instance, 'plone_utils')

    if event.transition.id == "activate":
        # A calculation cannot be re-activated if services it depends on
        # are deactivated.
        services = instance.getDependentServices()
        inactive_services = []
        for service in services:
            if wf.getInfoFor(service, "inactive_state") == "inactive":
                inactive_services.append(service.Title())
        if inactive_services:
            msg = _("Cannot activate calculation, because the following "
                    "service dependencies are inactive: ${inactive_services}",
                    mapping = {'inactive_services': ", ".join(inactive_services)})
            message = instance.translate(msg)
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException

    elif event.transition.id == "deactivate":
        # A calculation cannot be deactivated if active services are using it.
        services = bsc(portal_type="AnalysisService",
                       inactive_state="active")
        calc_services = []
        for service in services:
            service = service.getObject()
            calc = service.getCalculation()
            if calc and calc.UID() == instance.UID():
                calc_services.append(service.Title())
        if calc_services:
            msg = _('Cannot deactivate calculation, because it is in use by the '
                    'following services: ${calc_services}',
                    mapping = {'calc_services': ", ".join(calc_services)})
            message = instance.translate(msg)
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException
