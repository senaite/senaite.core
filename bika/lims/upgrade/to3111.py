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
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'cssregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'catalog')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'skins')

    """Update workflow permissions
    """
    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()

    reflex_rules(portal)
    return True


def reflex_rules(portal):
    at = getToolByName(portal, 'archetype_tool')
    # If reflex rules folder is not created yet, we should create it
    import pdb; pdb.set_trace()
    typestool = getToolByName(portal, 'portal_types')
    qi = portal.portal_quickinstaller
    if not portal['bika_setup'].get('bika_reflexrulefolder'):
        typestool.constructContent(type_name="ReflexRuleFolder",
                                   container=portal['bika_setup'],
                                   id='bika_reflexrulefolder',
                                   title='Reflex Rules Folder')
    obj = portal['bika_setup']['bika_reflexrulefolder']
    obj.unmarkCreationFlag()
    obj.reindexObject()
    if not portal['bika_setup'].get('bika_reflexrulefolder'):
        logger.info("ReflexRuleFolder not created")
    # Install Products.DataGridField
    qi.installProducts(['Products.DataGridField'])
    # add new types not to list in nav
    # ReflexRule
    portal_properties = getToolByName(portal, 'portal_properties')
    ntp = getattr(portal_properties, 'navtree_properties')
    types = list(ntp.getProperty('metaTypesNotToList'))
    types.append("ReflexRule")
    ntp.manage_changeProperties(MetaTypesNotToQuery=types)
