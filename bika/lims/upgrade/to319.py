from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import AddMultifile
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub
from bika.lims import logger


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.9
    """
    portal = aq_parent(aq_inner(tool))
    # Adding new feature multiple profiles per Analysis Request
    multipleAnalysisProfiles(portal)
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

    LIMS1546(portal)
    LIMS1558(portal)

    # Resort Invoices and AR Imports (LIMS-1908) in navigation bar
    portal.moveObjectToPosition('invoices', portal.objectIds().index('supplyorders'))
    portal.moveObjectToPosition('arimports', portal.objectIds().index('referencesamples'))
    return True


def multipleAnalysisProfiles(portal):
    """
    All the logic used to use multiple analysis profile selection in analysis request.
    We have to add some indexes and columns in setuphandler.py and also we have to move all analysis profiles from the
    analysis request's content field "profile" to profiles
    """
    bc = getToolByName(portal, 'bika_catalog', None)
    if 'getProfilesTitle' not in bc.indexes():
        bc.addIndex('getProfilesTitle', 'FieldIndex')
        bc.addColumn('getProfilesTitle')
    # Moving from profile to profiles
    ars = bc(portal_type="AnalysisRequest")
    for ar_brain in ars:
        ar = ar_brain.getObject()
        if not ar.getProfiles():
            ar.setProfiles(ar.getProfile())


def LIMS1546(portal):
    """Set catalogs for SRTemplate
    """
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('SRTemplate', ['bika_setup_catalog', 'portal_catalog'])
    for obj in portal.bika_setup.bika_srtemplates.objectValues():
        obj.unmarkCreationFlag()
        obj.reindexObject()


def LIMS1558(portal):
    """Setting Sampling rounds stuff
    """
    # Setting departments and ARtemplates to portal_catalog
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Department', ['bika_setup_catalog', "portal_catalog", ])
    at.setCatalogsByType('ARTemplate', ['bika_setup_catalog', 'portal_catalog'])
    for obj in portal.bika_setup.bika_departments.objectValues():
        obj.unmarkCreationFlag()
        obj.reindexObject()
    for obj in portal.bika_setup.bika_artemplates.objectValues():
        obj.unmarkCreationFlag()
        obj.reindexObject()
    # If Sampling rounds folder is not created yet, we should create it
    typestool = getToolByName(portal, 'portal_types')
    qi = portal.portal_quickinstaller
    if not portal['bika_setup'].get('bika_samplingrounds'):
        typestool.constructContent(type_name="SamplingRounds",
                                   container=portal['bika_setup'],
                                   id='bika_samplingrounds',
                                   title='Sampling Rounds')
    obj = portal['bika_setup']['bika_samplingrounds']
    obj.unmarkCreationFlag()
    obj.reindexObject()
    if not portal['bika_setup'].get('bika_samplingrounds'):
        logger.info("SamplingRounds not created")
    # Install Products.DataGridField
    qi.installProducts(['Products.DataGridField'])
    # add new types not to list in nav
    # SamplingRound
    portal_properties = getToolByName(portal, 'portal_properties')
    ntp = getattr(portal_properties, 'navtree_properties')
    types = list(ntp.getProperty('metaTypesNotToList'))
    types.append("SamplingRound")
    ntp.manage_changeProperties(MetaTypesNotToQuery=types)
