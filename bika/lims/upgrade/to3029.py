from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')

    # /supplyorders folder permissions
    mp = portal.supplyorders.manage_permission
    mp(CancelAndReinstate, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp(ManagePricelists, ['Manager', 'LabManager', 'Owner'], 1)
    mp(permissions.ListFolderContents, ['Member'], 1)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
    mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
    mp(permissions.View, ['Manager', 'LabManager'], 0)
    portal.supplyorders.reindexObject()

    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()

    return True
