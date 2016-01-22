from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from Products.CMFCore import permissions
from bika.lims.permissions import *


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.11
    """
    portal = aq_parent(aq_inner(tool))

    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '3111'))

    """Updated profile steps
    list of the generic setup import step names: portal.portal_setup.getSortedImportSteps() <---
    if you want more metadata use this: portal.portal_setup.getImportStepMetadata('jsregistry') <---
    important info about upgrade steps in
    http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps
    """
    setup = portal.portal_setup
    # setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    # setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    # setup.runImportStepFromProfile('profile-bika.lims:default', 'cssregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    # setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')
    # setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    # setup.runImportStepFromProfile('profile-bika.lims:default', 'catalog')
    # setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    # setup.runImportStepFromProfile('profile-bika.lims:default', 'skins')

    """Update workflow permissions
    """
    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()

    return True
