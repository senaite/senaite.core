from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import ManageWorksheets

def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # re-import js registry
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    # Update permissions according to Bika Setup
    # By default, restrict user access and management to WS
    bs = portal.bika_setup
    bs.setRestrictWorksheetUsersAccess(True)
    bs.setRestrictWorksheetManagement(True)
    bs.reindexObject()

    # Only LabManagers are able to create worksheets.
    mp = portal.manage_permission
    mp(ManageWorksheets, ['Manager', 'LabManager'],1)

    return True
