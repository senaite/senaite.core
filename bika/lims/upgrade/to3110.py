from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import AddMultifile
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub
from bika.lims import logger
from Products.CMFCore import permissions
from bika.lims.permissions import *


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.10
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    # Updated profile steps
    # list of the generic setup import step names: portal.portal_setup.getSortedImportSteps() <---
    # if you want more metadata use this: portal.portal_setup.getImportStepMetadata('jsregistry') <---
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'cssregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'catalog')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    # important info about upgrade steps in
    # http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'skins')
    # Update workflow permissions
    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()

    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '319'))

    # Migrations
    WINE119SupplyOrderPermissions(portal)

    return True


def WINE119SupplyOrderPermissions(portal):
    """LabClerk requires access to Supply Orders.
    """
    # AddSupplyOrder permission granted globally
    mp = portal.manage_permission
    mp(AddSupplyOrder, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)

    # Relax permissions of /supplyorders folder
    mp = portal.supplyorders.manage_permission
    mp(CancelAndReinstate, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
    mp(permissions.ListFolderContents, ['LabClerk', ''], 1)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
    mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
    portal.supplyorders.reindexObject()

    # AddSupplyOrder permission granted for specific clients
    for obj in portal.clients.objectValues():
        mp = obj.manage_permission
        mp(ManageSupplyOrders, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
