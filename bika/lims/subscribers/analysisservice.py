from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
import transaction

def ActionSucceededEventHandler(service, event):

    wf = getToolByName(service, 'portal_workflow')
    pc = getToolByName(service, 'portal_catalog')
    rc = getToolByName(service, 'reference_catalog')
    pu = getToolByName(service, 'plone_utils')

    if event.action == "deactivate":
        # A service cannot be deactivated if "active" calculations list it
        # as a dependency.
        calculations = (c.getObject() for c in pc(portal_type='Calculation'))
        for calc in calculations:
            deps = [dep.UID() for dep in calc.getDependentServices()]
            if service.UID() in deps:
                message = _("This Analysis Service cannot be deactivated "
                            "because one or more active calaculations list "
                            "it as a dependency")
                pu.addPortalMessage(message, 'error')
                transaction.get().abort()
                raise WorkflowException
