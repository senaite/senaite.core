from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
import transaction

def ActionSucceededEventHandler(instance, event):

    wf = getToolByName(instance, 'portal_workflow')
    pc = getToolByName(instance, 'portal_catalog')
    rc = getToolByName(instance, 'reference_catalog')
    pu = getToolByName(instance, 'plone_utils')
    ts = getToolByName(instance, 'translation_service')

    if event.action == "activate":
        # A calculation cannot be re-activated if services it depends on
        # are deactivated.
        services = instance.getDependentServices()
        inactive_services = []
        for service in services:
            if wf.getInfoFor(service, "inactive_review_state") == "inactive":
                inactive_services.append(service.Title())
        if inactive_services:
            message = ts.translate(
                "message_calculation_reactivate_deps_not_active",
                "bika",
                {'inactive_services': ", ".join(inactive_services)},
                instance,
                default = "Cannot activate calculation, because the following " \
                          "service dependencies are inactive: ${inactive_services}")
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException

    if event.action == "deactivate":
        # A calculation cannot be deactivated if active services are using it.
        services = pc(portal_type="AnalysisService", inactive_review_state="active")
        calc_services = []
        for service in services:
            service = service.getObject()
            calc = service.getCalculation()
            if calc and calc.UID() == instance.UID():
                calc_services.append(service.Title())
        if calc_services:
            message = ts.translate(
                "message_calculation_deactivate_in_use",
                "bika",
                {'calc_services': ", ".join(calc_services)},
                instance,
                default = "Cannot deactivate calculation, because it is " \
                          "in use by the following services: ${calc_services}")
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException
