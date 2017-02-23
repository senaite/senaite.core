# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType

from bika.lims import logger
from Products.CMFCore import permissions
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils import tmpID
from bika.lims.permissions import *
from bika.lims.utils import tmpID
from bika.lims.catalog import setup_catalogs
from bika.lims.catalog import getCatalogDefinitions
import traceback
import sys
import transaction


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.2.0
    """
    portal = aq_parent(aq_inner(tool))

    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '3.2.0'))

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
    setup.runImportStepFromProfile('profile-bika.lims:default', 'toolset')
    setup.runImportStepFromProfile(
        'profile-bika.lims:default', 'portlets', run_dependencies=False)

    # Creating all the sampling coordinator roles, permissions and indexes
    logger.info("Sampling Coordinator...")
    create_samplingcoordinator(portal)

    # Reflex Testing setup
    logger.info("Reflex testing...")
    reflex_rules(portal)

    # Departments
    logger.info("Departments...")
    departments(portal)

    # More than one department can be assigned to a Contact
    logger.info("More than one department per contact...")
    multi_department_to_labcontact(portal)

    # Migrate Instrument Locations
    logger.info("Migrating instrument locations...")
    migrate_instrument_locations(portal)

    # Updating Verifications of Analysis field from integer to String.
    logger.info("Multiverification of Analyses...")
    multi_verification(portal)

    # Adding old method of instrument as a set .
    logger.info("Assigning Multiple method to instruments...")
    instrument_multiple_methods(portal)

    # Update workflow permissions
    try:
        logger.info("Updating role mappings...")
        wf = getToolByName(portal, 'portal_workflow')
        wf.updateRoleMappings()
    except:
        logger.error(traceback.format_exc())
        e = sys.exc_info()
        logger.error("Unable to update role maps due to: %s" % (str(e)))

    # Remove unused indexes and columns
    logger.info("Removing stale indexes...")
    bc = getToolByName(portal, 'bika_catalog', None)
    delIndexAndColumn(bc, 'getProfilesTitle')

    # Adding two columns for client data
    addColumnsForClient(portal)

    # Adding getAnalysisRequestUID column in analysis catalog
    addgetAnalysisRequestUID(portal)
    # Adding getBatchUID column in analysis catalog
    addgetBatchUID(portal)
    # Adding getSampleConditionUID column in analysis catalog
    addgetSampleConditionUID(portal)
    # Adding getAnalysisRequestPrintStatus column in analysis catalog
    addgetAnalysisRequestPrintStatus(portal)

    # Clean and rebuild affected catalogs (if required)
    logger.info("Cleaning and rebuilding...")
    cleanAndRebuildIfNeeded(portal)
    # Updating lims catalogs if there is any change in them
    logger.info("Updating catalogs if needed...")
    setup_catalogs(portal, getCatalogDefinitions())
    logger.info("Catalogs updated")

    return True


def migrate_instrument_locations(portal):
    bsc = portal.bika_setup_catalog

    bika_instrumentlocations = portal.bika_setup.get("bika_instrumentlocations")

    if bika_instrumentlocations is None:
        logger.error("bika_instrumentlocations not found in bika_setup!")
        return  # This should not happen

    # move bika_instrumentlocations below bika_instrumenttypes
    panel_ids = portal.bika_setup.objectIds()
    target_idx = panel_ids.index("bika_instrumenttypes")
    current_idx = panel_ids.index("bika_instrumentlocations")
    delta = current_idx - target_idx
    if delta > 1:
        portal.bika_setup.moveObjectsUp("bika_instrumentlocations", delta=delta-1)

    instrument_brains = bsc(portal_type="Instrument")
    for instrument_brain in instrument_brains:
        instrument = instrument_brain.getObject()

        # get the string value of the `location` field
        location = instrument.getLocation()
        if not location:
            continue  # Skip if no location was set

        # make a dictionary with the Titles as keys and the objects as values
        instrument_locations = bika_instrumentlocations.objectValues()
        instrument_location_titles = map(lambda o: o.Title(), instrument_locations)
        locations = dict(zip(instrument_location_titles, instrument_locations))

        instrument_location = None
        if location in locations:
            logger.info("Instrument Location {} exists in bika_instrumentlocations".format(location))
            instrument_location = locations[location]
        else:
            # Create a new location and link it to the instruments InstrumentLocation field
            instrument_location = _createObjectByType("InstrumentLocation", bika_instrumentlocations, tmpID())
            instrument_location.setTitle(location)
            instrument_location._renameAfterCreation()
            instrument_location.reindexObject()
            logger.info("Created Instrument Location {} in bika_instrumentlocations".format(location))

        instrument.setLocation(None)  # flush the old instrument location
        instrument.setInstrumentLocation(instrument_location)
        instrument.reindexObject()
        logger.info("Linked Instrument Location {} to Instrument {}".format(location, instrument.id))
    transaction.commit()


def create_samplingcoordinator(portal):
    # Creates the new group
    portal_groups = portal.portal_groups
    if 'SamplingCoordinator'\
            not in portal.acl_users.portal_role_manager.listRoleIds():
        portal.acl_users.portal_role_manager.addRole('SamplingCoordinator')
        # add roles to the portal
        portal._addRole('SamplingCoordinator')
        if 'SamplingCoordinators' not in portal_groups.listGroupIds():
            portal_groups.addGroup(
                'SamplingCoordinators', title="Sampling Coordinators",
                roles=['SamplingCoordinator'])

        # permissions
        # to deal with permissions http://docs.plone.org/develop/plone/security/permissions.html#checking-if-the-logged-in-user-has-a-permission
        # Root permissions
        # The last 0/1 regards the 'Acquire' column in the workflow's csv's
        mp = portal.manage_permission
        mp(AddSamplePartition, ['Manager', 'Owner', 'LabManager', 'LabClerk', 'Sampler', 'SamplingCoordinator'], 1)
        mp(ManageARPriority, ['Manager', 'LabManager', 'LabClerk'], 1)
        mp(ManageAnalysisRequests, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'RegulatoryInspector', 'SamplingCoordinator'], 1)
        mp(ManageSamples, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'RegulatoryInspector', 'SamplingCoordinator'], 1)
        mp(ScheduleSampling, ['Manager', 'SamplingCoordinator'], 0)
        mp(ReceiveSample, ['Manager', 'LabManager', 'LabClerk', 'Sampler', 'SamplingCoordinator'], 1)
        mp(EditSample, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'SamplingCoordinator'], 1)
        mp(ViewResults, ['Manager', 'LabManager', 'Analyst', 'Sampler', 'RegulatoryInspector', 'SamplingCoordinator'], 1)
        mp(EditSamplePartition, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'SamplingCoordinator'], 1)

        # /clients folder permissions
        mp = portal.clients.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'SamplingCoordinator'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Member', 'Analyst', 'Sampler', 'Preserver', 'SamplingCoordinator', 'SamplingCoordinator'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'SamplingCoordinator'], 0)
        portal.clients.reindexObject()
        for obj in portal.clients.objectValues():
            mp = obj.manage_permission
            mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'SamplingCoordinator'], 0)
            mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Member', 'Analyst', 'Sampler', 'Preserver', 'SamplingCoordinator'], 0)
            mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'SamplingCoordinator'], 0)
            obj.reindexObject()
            for contact in portal.clients.objectValues('Contact'):
                mp = contact.manage_permission
                mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Owner', 'Analyst', 'Sampler', 'Preserver', 'SamplingCoordinator'], 0)
                mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner', 'SamplingCoordinator'], 0)

        # /analysisrequests folder permissions
        mp = portal.analysisrequests.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'RegulatoryInspector', 'SamplingCoordinator'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'RegulatoryInspector', 'SamplingCoordinator'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'RegulatoryInspector', 'SamplingCoordinator'], 0)
        portal.analysisrequests.reindexObject()

        # /samples folder permissions
        mp = portal.samples.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector', 'SamplingCoordinator'], 0)
        mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'SamplingCoordinator'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector', 'SamplingCoordinator'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector', 'SamplingCoordinator'], 0)
        portal.samples.reindexObject()
        transaction.commit()

    # Add the index for the catalog
    bc = getToolByName(portal, 'bika_catalog', None)
    addIndex(bc, 'getScheduledSamplingSampler', 'FieldIndex')
    transaction.commit()


def departments(portal):
    """ To add department indexes to the catalogs """
    bc = getToolByName(portal, 'bika_catalog')
    bac = getToolByName(portal, 'bika_analysis_catalog')
    addIndex(bc, 'getDepartmentUIDs', 'KeywordIndex')
    addIndex(bac, 'getDepartmentUID', 'KeywordIndex')
    transaction.commit()


def addColumnsForClient(portal):
    """
    Add columns to portal catalog in order to use them in
    analysisrequests listings.
    """
    pc = getToolByName(portal, 'portal_catalog')
    addColumn(pc, 'getProvince')
    addColumn(pc, 'getDistrict')
    transaction.commit()


def addgetAnalysisRequestUID(portal):
    """
    Add an index to analysis catalog in order to use them in
    analysisrequests listings.
    """
    catalog = getToolByName(portal, 'bika_analysis_catalog')
    addIndex(catalog, 'getAnalysisRequestUID', 'FieldIndex')
    transaction.commit()


def addgetBatchUID(portal):
    """
    Add an index to analysis catalog in order to use them in
    analysisrequests listings.
    """
    catalog = getToolByName(portal, 'bika_analysis_catalog')
    addIndex(catalog, 'getBatchUID', 'FieldIndex')
    transaction.commit()


def addgetSampleConditionUID(portal):
    """
    Add an index to analysis catalog in order to use them in
    analysisrequests listings.
    """
    catalog = getToolByName(portal, 'bika_analysis_catalog')
    addIndex(catalog, 'getSampleConditionUID', 'FieldIndex')
    transaction.commit()


def addgetAnalysisRequestPrintStatus(portal):
    """
    Add an index to analysis catalog in order to use them in
    analysisrequests listings.
    """
    catalog = getToolByName(portal, 'bika_analysis_catalog')
    addIndex(catalog, 'getAnalysisRequestPrintStatus', 'FieldIndex')
    transaction.commit()


def create_CAS_IdentifierType(portal):
    """LIMS-1391 The CAS Nr IdentifierType is normally created by
    setuphandlers during site initialisation.
    """
    bsc = getToolByName(portal, 'bika_catalog', None)
    idtypes = bsc(portal_type = 'IdentifierType', title='CAS Nr')
    if not idtypes:
        folder = portal.bika_setup.bika_identifiertypes
        idtype = _createObjectByType('IdentifierType', folder, tmpID())
        idtype.processForm()
        idtype.edit(title='CAS Nr',
                    description='Chemical Abstracts Registry number',
                    portal_types=['Analysis Service'])
    transaction.commit()


def multi_verification(portal):
    """
    Getting all analyses with review_state in to_be_verified and
    adding "admin" as a verificator as many times as this analysis verified before.
    """
    pc = getToolByName(portal, 'portal_catalog', None)
    objs = pc(portal_type="Analyses", review_state="to_be_verified")
    for obj_brain in objs:
        obj = obj_brain.getObject()
        old_field = obj.Schema().get("NumberOfVerifications", None).get(obj)
        if old_field:
            new_value = ''
            for n in range(0, old_field):
                new_value += 'admin'
                if n < old_field:
                    new_value += ','
            obj.setVerificators(new_value)
    transaction.commit()


def reflex_rules(portal):
    at = getToolByName(portal, 'archetype_tool')
    # If reflex rules folder is not created yet, we should create it
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

    pc = getToolByName(portal, 'portal_catalog')
    addIndex(pc, 'worksheettemplateUID', 'FieldIndex')
    addIndexAndColumn(pc, 'Analyst', 'FieldIndex')

    bsc = getToolByName(portal, 'bika_setup_catalog')
    addIndex(bsc, 'getAvailableMethodsUIDs', 'KeywordIndex')
    addIndex(bsc, 'getMethodUID', 'FieldIndex')

    bac = getToolByName(portal, 'bika_analysis_catalog')
    addIndex(bac, 'getInstrumentUID', 'FieldIndex')
    addIndex(bac, 'getMethodUID', 'FieldIndex')
    addIndex(bac, 'getInstrumentUID', 'FieldIndex')
    transaction.commit()


def multi_department_to_labcontact(portal):
    """
    In "Lab Contact" edit view, replace the selection list populated with
    departments by a multi-select list.
    This requires to create a new content field on order to deal with
    the migration of the old single-select list.
    The 'Department' field info from created objects should be migrated to the
    multi-select field 'Departments' to maintain the consistency
    """
    pc = getToolByName(portal, 'portal_catalog', None)
    # Moving from profile to profiles
    objs = pc(portal_type="LabContact")
    for obj_brain in objs:
        obj = obj_brain.getObject()
        if not obj.getDepartments():
            obj.setDepartments(obj.getDepartment())
    transaction.commit()


def instrument_multiple_methods(portal):
    # An instrument had only a single relevant field called "Method".
    # This field has been replaced with a multiValued "Methods" field.

    # First adding new index
    bsc = getToolByName(portal, 'bika_setup_catalog')
    addIndex(bsc, 'getMethodUIDs', 'KeywordIndex')

    for instrument in portal.bika_setup.bika_instruments.objectValues():
        value = instrument.Schema().get("Method", None).get(instrument)
        if value:
            instrument.setMethods([value])
    transaction.commit()


# *********************
# Helper methods below
# *********************
cleanrebuild = []
def delIndexAndColumn(catalog, index):
    if index in catalog.indexes():
        try:
            catalog.delIndex(index)
            logger.info('Old catalog index %s deleted.' % index)
            if catalog.id not in cleanrebuild:
                cleanrebuild.append(catalog.id)
        except:
            pass
        try:
            catalog.delColumn(index)
            logger.info('Old catalog column %s deleted.' % index)
        except:
            pass

def addIndex(catalog, index, indextype):
    if index not in catalog.indexes():
        try:
            catalog.addIndex(index, indextype)
            logger.info('Catalog index %s added.' % index)
            if catalog.id not in cleanrebuild:
                cleanrebuild.append(catalog.id)
        except:
            pass


def addColumn(cat, col):
    if col not in cat.schema():
        try:
            cat.addColumn(col)
            logger.info('Column %s added to %s.' % (col, cat.id))
            if catalog.id not in cleanrebuild:
                cleanrebuild.append(catalog.id)
        except:
            logger.error(
                'Catalog column %s error while adding to %s.' % (col, cat.id))


def addIndexAndColumn(catalog, index, indextype):
    if index not in catalog.indexes():
        try:
            catalog.addIndex(index, indextype)
            logger.info('Catalog index %s added.' % index)
            if catalog.id not in cleanrebuild:
                cleanrebuild.append(catalog.id)
        except:
            pass
        try:
            catalog.addColumn(index)
            logger.info('Catalog column %s added.' % index)
        except:
            pass

def cleanAndRebuildIfNeeded(portal):
    for c in cleanrebuild:
        try:
            catalog = getToolByName(portal, c)
            catalog.clearFindAndRebuild()
        except:
            logger.info("Unable to clean and rebuild %s " % c)
            pass
        transaction.commit()
