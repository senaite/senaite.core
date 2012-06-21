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

    if event.transition.id == "deactivate":
        # A service cannot be deactivated if "active" calculations list it
        # as a dependency.
        calculations = (c.getObject() for c in \
                        bsc(portal_type='Calculation', inactive_state="active"))
        for calc in calculations:
            deps = [dep.UID() for dep in calc.getDependentServices()]
            if instance.UID() in deps:
                message = _("This Analysis Service cannot be deactivated "
                            "because one or more active calculations list "
                            "it as a dependency")
                pu.addPortalMessage(message, 'error')
                transaction.get().abort()
                raise WorkflowException

    elif event.transition.id == "activate":
        # A service cannot be activated if it's calculation is inactive
        calc = instance.getCalculation()
        if calc and \
           wf.getInfoFor(calc, "inactive_state") == "inactive":
            message = _("This Analysis Service cannot be activated "
                        "because it's calculation is inactive.")
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException
