from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')

    # /orders folder permissions
    mp = portal.orders.manage_permission
    mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp(ManagePricelists, ['Manager', 'LabManager', 'Owner'], 1)
    mp(permissions.ListFolderContents, ['Member'], 1)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
    mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
    mp(permissions.View, ['Manager', 'LabManager'], 0)
    portal.orders.reindexObject()

    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()

    return True
