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
    setup.runImportStepFromProfile('profile-bika.lims:default', 'factorytool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'controlpanel')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'catalog')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'skins')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile(
        'profile-bika.lims:default', 'portlets', run_dependencies=False)
    # Creating all the sampling coordinator roles, permissions and indexes
    create_samplingcoordinator(portal)
    departments(portal)
    departments(portal)
    # Migrate Instrument Locations
    migrate_instrument_locations(portal)
    """Update workflow permissions
    """
    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()
    # Updating Verifications of Analysis field from integer to String.
    multi_verification(portal)

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
    portal.analysisrequests.reindexObject()

    # Add the index for the catalog
    bc = getToolByName(portal, 'bika_catalog', None)
    if 'getScheduledSamplingSampler' not in bc.indexes():
        bc.addIndex('getScheduledSamplingSampler', 'FieldIndex')

        bac.clearFindAndRebuild()

def departments(portal):
    """ To add department indexes to the catalogs """
    bc = getToolByName(portal, 'bika_catalog')
    if 'getDepartmentUIDs' not in bc.indexes():
        bc.addIndex('getDepartmentUIDs', 'KeywordIndex')
        bc.clearFindAndRebuild()
    bac = getToolByName(portal, 'bika_analysis_catalog')
    if 'getDepartmentUID' not in bac.indexes():
        bac.addIndex('getDepartmentUID', 'KeywordIndex')

def create_CAS_IdentifierType(portal):
    """LIMS-1391 The CAS Nr IdentifierType is normally created by
    setuphandlers during site initialisation.
    """
    pc = getToolByName(portal, 'portal_catalog', None)
    objs = pc(portal_type="Analyses",review_state="to_be_verified")
    for obj_brain in objs:
        obj = obj_brain.getObject()
        old_field = obj.Schema().get("NumberOfVerifications", None)
        if old_field:
            new_value=''
            for n in range(0,old_field):
                new_value+='admin'
    bsc = getToolByName(portal, 'bika_catalog', None)
    idtypes = bsc(portal_type = 'IdentifierType', title='CAS Nr')
    if not idtypes:
        folder = portal.bika_setup.bika_identifiertypes
        idtype = _createObjectByType('IdentifierType', folder, tmpID())
        idtype.processForm()
        idtype.edit(title='CAS Nr',
                    description='Chemical Abstracts Registry number',
                    portal_types=['Analysis Service'])

def multi_verification(portal):
    """
    Getting all analyses with review_state in to_be_verified and
    adding "admin" as a verificator as many times as this analysis verified before.
    """
    pc = getToolByName(portal, 'portal_catalog', None)
    objs = pc(portal_type="Analyses",review_state="to_be_verified")
    for obj_brain in objs:
        obj = obj_brain.getObject()
        old_field = obj.Schema().get("NumberOfVerifications", None)
        if old_field:
            new_value=''
            for n in range(0,old_field):
                new_value+='admin'
                if n<old_field:
                    new_value+=','
            obj.setVerificators(new_value)

