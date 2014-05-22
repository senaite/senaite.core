from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import ManageWorksheets

def upgrade(tool):
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
