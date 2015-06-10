from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import AddMultifile
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub
from bika.lims import logger

def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.8
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '318'))

    # Updated profile steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')

    # Adding Multifile content type
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Multifile', ['bika_setup_catalog', ])

    # Adding indexes
    bsc = getToolByName(portal, 'bika_setup_catalog', None)
    if 'getMethodID' not in bsc.indexes():
        bsc.addIndex('getMethodID', 'FieldIndex')
    if 'getDocumentID' not in bsc.indexes():
        bsc.addIndex('getDocumentID', 'FieldIndex')

    # Define permissions for Multifile
    mp = portal.manage_permission
    mp(AddMultifile, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)
    # Update workflow permissions
    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()


    # Migrations
    HEALTH245(portal)

    return True

def HEALTH245(portal):
    """ Set the '-' as default separator in all ids. Otherwise, new
        records will be created without '-', which has been used since
        now by default
    """
    for p in portal.bika_setup.getPrefixes():
        p['separator']='-' if (not p.get('separator', None)) else p['separator']
