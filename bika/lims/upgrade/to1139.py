from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import permissions
from bika.lims.permissions import *

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    wf = portal.portal_workflow
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    wf.updateRoleMappings()

    # Reset batch statuses to new ones
    portal_catalog = getToolByName(portal, 'portal_catalog')
    wf = getToolByName(portal, 'portal_workflow')
    proxies = portal_catalog(portal_type="Batch")
    for proxy in proxies:
        batch = proxy.getObject()
        rvwstate = wf.getInfoFor(batch, 'review_state', 'open')
        invstate = wf.getInfoFor(batch, 'cancellation_state', '')
        if rvwstate != 'open' and rvwstate != 'closed':
            # First cancel the batches (to avoid the guards)
            try:
                wf.doActionFor(batch, 'cancel')
            except WorkflowException:
                pass

        if invstate == 'cancelled':
            try:
                wf.doActionFor(batch, 'cancel')
            except WorkflowException:
                pass

        elif rvwstate != 'closed':
            try:
                wf.doActionFor(batch, 'open')
            except WorkflowException:
                pass

    return True
