"""Upgrades an instance from rc3.4 (1104) to rc3.5 (1105)."""

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from bika.lims.setuphandlers import BikaGenerator
from bika.lims import logger


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    bc = getToolByName(portal, 'bika_catalog')
    bac = getToolByName(portal, 'bika_analysis_catalog')
    pc = getToolByName(portal, 'portal_catalog')
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    wf = getToolByName(portal, 'portal_workflow')

    # Update all tools in which changes have been made
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'repositorytool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'portlets', run_dependencies=False)
    setup.runImportStepFromProfile('profile-bika.lims:default', 'viewlets')
    setup.runImportStepFromProfile('profile-plone.app.jquery:default', 'jsregistry')

    # Re-import the default permission maps
    gen = BikaGenerator()
    gen.setupPermissions(portal)

    logger.info("Updating workflow role/permission mappings")
    wf.updateRoleMappings()
    logger.info("Rebuilding portal_catalog")
    pc.clearFindAndRebuild()
    logger.info("Rebuilding bika_analysis_catalog")
    bac.clearFindAndRebuild()
    logger.info("Rebuilding bika_catalog")
    bc.clearFindAndRebuild()

    return True
