# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

""" Bika setup handlers. """

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.catalog import getCatalogDefinitions
from bika.lims.catalog import setup_catalogs
from bika.lims.config import *
from bika.lims.interfaces import IARImportFolder, IHaveNoBreadCrumbs
from bika.lims.permissions import setup_permissions
from bika.lims.utils import tmpID
from zope.interface import alsoProvides


# noinspection PyClassHasNoInit
class Empty:
    pass


class BikaGenerator(object):
    def __init__(self):
        pass

    def setupPortalContent(self, portal):
        """ Setup Bika site structure """
        self.fix_frontpage_permissions(portal)
        self.remove_default_content(portal)
        self.reindex_structure(portal)

        portal.bika_setup.laboratory.unmarkCreationFlag()
        portal.bika_setup.laboratory.reindexObject()

    def reindex_structure(self, portal):
        # index objects - importing through GenericSetup doesn't
        for obj_id in ('clients',
                       'batches',
                       'invoices',
                       'pricelists',
                       'bika_setup',
                       'methods',
                       'analysisrequests',
                       'referencesamples',
                       'samples',
                       'supplyorders',
                       'worksheets',
                       'reports',
                       'arimports',
                       ):
            try:
                obj = portal[obj_id]
                obj.unmarkCreationFlag()
                obj.reindexObject()
            except AttributeError:
                pass

        for obj_id in ('bika_analysiscategories',
                       'bika_analysisservices',
                       'bika_attachmenttypes',
                       'bika_batchlabels',
                       'bika_calculations',
                       'bika_departments',
                       'bika_containers',
                       'bika_containertypes',
                       'bika_preservations',
                       'bika_identifiertypes',
                       'bika_instruments',
                       'bika_instrumenttypes',
                       'bika_instrumentlocations',
                       'bika_analysisspecs',
                       'bika_analysisprofiles',
                       'bika_artemplates',
                       'bika_labcontacts',
                       'bika_labproducts',
                       'bika_manufacturers',
                       'bika_sampleconditions',
                       'bika_samplematrices',
                       'bika_samplingdeviations',
                       'bika_samplepoints',
                       'bika_sampletypes',
                       'bika_srtemplates',
                       'bika_reflexrulefolder',
                       'bika_storagelocations',
                       'bika_subgroups',
                       'bika_suppliers',
                       'bika_referencedefinitions',
                       'bika_worksheettemplates'):
            try:
                obj = portal.bika_setup[obj_id]
                obj.unmarkCreationFlag()
                obj.reindexObject()
            except AttributeError:
                pass

    def remove_default_content(self, portal):
        # remove undesired content objects
        del_ids = []
        for obj_id in ['Members', 'news', 'events']:
            if obj_id in portal:
                del_ids.append(obj_id)
        if del_ids:
            portal.manage_delObjects(ids=del_ids)

    def fix_frontpage_permissions(self, portal):
        if 'front-page' in portal:
            obj = portal['front-page']
            alsoProvides(obj, IHaveNoBreadCrumbs)
            mp = obj.manage_permission
            mp(permissions.View, ['Anonymous'], 1)

    def setupGroupsAndRoles(self, portal):
        # add roles
        for role in ('LabManager',
                     'LabClerk',
                     'Analyst',
                     'Verifier',
                     'Sampler',
                     'Preserver',
                     'Publisher',
                     'Member',
                     'Reviewer',
                     'RegulatoryInspector',
                     'Client',
                     'SamplingCoordinator'):
            if role not in portal.acl_users.portal_role_manager.listRoleIds():
                portal.acl_users.portal_role_manager.addRole(role)
            # add roles to the portal
            portal._addRole(role)

        # Create groups
        portal_groups = portal.portal_groups

        if 'LabManagers' not in portal_groups.listGroupIds():
            try:
                portal_groups.addGroup('LabManagers', title="Lab Managers",
                                       roles=['Member', 'LabManager',
                                              'Site Administrator', ])
            except KeyError:
                portal_groups.addGroup('LabManagers', title="Lab Managers",
                                       roles=['Member', 'LabManager',
                                              'Manager', ])  # Plone < 4.1

        if 'LabClerks' not in portal_groups.listGroupIds():
            portal_groups.addGroup('LabClerks', title="Lab Clerks",
                                   roles=['Member', 'LabClerk'])

        if 'Analysts' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Analysts', title="Lab Technicians",
                                   roles=['Member', 'Analyst'])

        if 'Verifiers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Verifiers', title="Verifiers",
                                   roles=['Verifier'])

        if 'Samplers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Samplers', title="Samplers",
                                   roles=['Sampler'])

        if 'Preservers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Preservers', title="Preservers",
                                   roles=['Preserver'])

        if 'Publishers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Publishers', title="Publishers",
                                   roles=['Publisher'])

        if 'Clients' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Clients', title="Clients",
                                   roles=['Member', 'Client'])

        if 'Suppliers' not in portal_groups.listGroupIds():
            portal_groups.addGroup('Suppliers', title="",
                                   roles=['Member', ])

        if 'RegulatoryInspectors' not in portal_groups.listGroupIds():
            portal_groups.addGroup('RegulatoryInspectors',
                                   title="Regulatory Inspectors",
                                   roles=['Member', 'RegulatoryInspector'])

        if 'SamplingCoordinators' not in portal_groups.listGroupIds():
            portal_groups.addGroup(
                'SamplingCoordinators', title="Sampling Coordinators",
                roles=['SamplingCoordinator'])

    def setupPermissions(self, portal):
        """ Set up some suggested role to permission mappings.
        """
        setup_permissions(portal)

    def setupVersioning(self, portal):
        try:
            # noinspection PyUnresolvedReferences
            from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES
        except ImportError:
            return
        portal_repository = getToolByName(portal, 'portal_repository')
        versionable_types = list(portal_repository.getVersionableContentTypes())

        for type_id in VERSIONABLE_TYPES:
            if type_id not in versionable_types:
                versionable_types.append(type_id)
                # Add default versioning policies to the versioned type
                for policy_id in DEFAULT_POLICIES:
                    portal_repository.addPolicyForContentType(
                        type_id, policy_id)
        portal_repository.setVersionableContentTypes(versionable_types)

    def setupCatalogs(self, portal):
        # an item should belong to only one catalog.
        # that way looking it up means first looking up *the* catalog
        # in which it is indexed, as well as making it cheaper to index.

        def addIndex(cat, *args):
            # noinspection PyBroadException
            try:
                cat.addIndex(*args)
            except:
                pass

        def addColumn(cat, col):
            # noinspection PyBroadException
            try:
                cat.addColumn(col)
            except:
                pass

        # create lexicon
        wordSplitter = Empty()
        wordSplitter.group = 'Word Splitter'
        wordSplitter.name = 'Unicode Whitespace splitter'
        caseNormalizer = Empty()
        caseNormalizer.group = 'Case Normalizer'
        caseNormalizer.name = 'Unicode Case Normalizer'
        stopWords = Empty()
        stopWords.group = 'Stop Words'
        stopWords.name = 'Remove listed and single char words'
        elem = [wordSplitter, caseNormalizer, stopWords]
        zc_extras = Empty()
        zc_extras.index_type = 'Okapi BM25 Rank'
        zc_extras.lexicon_id = 'Lexicon'

        # bika_catalog

        bc = getToolByName(portal, 'bika_catalog', None)
        if bc is None:
            logger.warning('Could not find the bika_catalog tool.')
            return

        # noinspection PyBroadException
        try:
            bc.manage_addProduct['ZCTextIndex'].manage_addLexicon(
                'Lexicon', 'Lexicon', elem)
        except:
            logger.warning('Could not add ZCTextIndex to bika_catalog')
            pass

        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('Batch', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('Sample', ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('SamplePartition',
                             ['bika_catalog', 'portal_catalog'])
        at.setCatalogsByType('ReferenceSample',
                             ['bika_catalog', 'portal_catalog'])

        addIndex(bc, 'path', 'ExtendedPathIndex', 'getPhysicalPath')
        addIndex(bc, 'allowedRolesAndUsers', 'KeywordIndex')
        addIndex(bc, 'UID', 'FieldIndex')
        addIndex(bc, 'SearchableText', 'ZCTextIndex', zc_extras)
        addIndex(bc, 'Title', 'ZCTextIndex', zc_extras)
        addIndex(bc, 'Description', 'ZCTextIndex', zc_extras)
        addIndex(bc, 'id', 'FieldIndex')
        addIndex(bc, 'getId', 'FieldIndex')
        addIndex(bc, 'Type', 'FieldIndex')
        addIndex(bc, 'portal_type', 'FieldIndex')
        addIndex(bc, 'created', 'DateIndex')
        addIndex(bc, 'Creator', 'FieldIndex')
        addIndex(bc, 'getObjPositionInParent', 'GopipIndex')
        addIndex(bc, 'title', 'FieldIndex', 'Title')
        addIndex(bc, 'sortable_title', 'FieldIndex')
        addIndex(bc, 'description', 'FieldIndex', 'Description')
        addIndex(bc, 'review_state', 'FieldIndex')
        addIndex(bc, 'inactive_state', 'FieldIndex')
        addIndex(bc, 'worksheetanalysis_review_state', 'FieldIndex')
        addIndex(bc, 'cancellation_state', 'FieldIndex')
        addIndex(bc, 'Identifiers', 'KeywordIndex')

        addIndex(bc, 'getDepartmentUIDs', 'KeywordIndex')
        addIndex(bc, 'getAnalysisService', 'KeywordIndex')
        addIndex(bc, 'getAnalyst', 'FieldIndex')
        addIndex(bc, 'getAnalysts', 'KeywordIndex')
        addIndex(bc, 'getAnalysesUIDs', 'KeywordIndex')
        addIndex(bc, 'BatchDate', 'DateIndex')
        addIndex(bc, 'getClientOrderNumber', 'FieldIndex')
        addIndex(bc, 'getClientReference', 'FieldIndex')
        addIndex(bc, 'getClientSampleID', 'FieldIndex')
        addIndex(bc, 'getClientTitle', 'FieldIndex')
        addIndex(bc, 'getClientUID', 'FieldIndex')
        addIndex(bc, 'getContactTitle', 'FieldIndex')
        addIndex(bc, 'getDateDisposed', 'DateIndex')
        addIndex(bc, 'getDateExpired', 'DateIndex')
        addIndex(bc, 'getDateOpened', 'DateIndex')
        addIndex(bc, 'getDatePublished', 'DateIndex')
        addIndex(bc, 'getDateReceived', 'DateIndex')
        addIndex(bc, 'getDateSampled', 'DateIndex')
        addIndex(bc, 'getDisposalDate', 'DateIndex')
        addIndex(bc, 'getDueDate', 'DateIndex')
        addIndex(bc, 'getExpiryDate', 'DateIndex')
        addIndex(bc, 'getInvoiced', 'FieldIndex')
        addIndex(bc, 'getPreserver', 'FieldIndex')
        addIndex(bc, 'getReferenceDefinitionUID', 'FieldIndex')
        addIndex(bc, 'getSampleID', 'FieldIndex')
        addIndex(bc, 'getSamplePointTitle', 'FieldIndex')
        addIndex(bc, 'getSamplePointUID', 'FieldIndex')
        addIndex(bc, 'getSampler', 'FieldIndex')
        addIndex(bc, 'getScheduledSamplingSampler', 'FieldIndex')
        addIndex(bc, 'getSampleTypeTitle', 'FieldIndex')
        addIndex(bc, 'getSampleTypeUID', 'FieldIndex')
        addIndex(bc, 'getSampleUID', 'FieldIndex')
        addIndex(bc, 'getSamplingDate', 'DateIndex')
        addIndex(bc, 'getWorksheetTemplateTitle', 'FieldIndex')
        addIndex(bc, 'BatchUID', 'FieldIndex')
        addColumn(bc, 'path')
        addColumn(bc, 'UID')
        addColumn(bc, 'id')
        addColumn(bc, 'getId')
        addColumn(bc, 'Type')
        addColumn(bc, 'portal_type')
        addColumn(bc, 'creator')
        addColumn(bc, 'Created')
        addColumn(bc, 'Title')
        addColumn(bc, 'Description')
        addColumn(bc, 'sortable_title')
        addColumn(bc, 'review_state')
        addColumn(bc, 'inactive_state')
        addColumn(bc, 'cancellation_state')
        addColumn(bc, 'getAnalysts')
        addColumn(bc, 'getSampleID')
        addColumn(bc, 'getClientOrderNumber')
        addColumn(bc, 'getClientReference')
        addColumn(bc, 'getClientSampleID')
        addColumn(bc, 'getContactTitle')
        addColumn(bc, 'getClientTitle')
        addColumn(bc, 'getSamplePointTitle')
        addColumn(bc, 'getSampleTypeTitle')
        addColumn(bc, 'getAnalysisService')
        addColumn(bc, 'getDatePublished')
        addColumn(bc, 'getDateReceived')
        addColumn(bc, 'getDateSampled')
        addColumn(bc, 'review_state')

        # bika_setup_catalog

        bsc = getToolByName(portal, 'bika_setup_catalog', None)
        if bsc is None:
            logger.warning('Could not find the setup catalog tool.')
            return

        # noinspection PyBroadException
        try:
            bsc.manage_addProduct['ZCTextIndex'].manage_addLexicon(
                'Lexicon', 'Lexicon', elem)
        except:
            logger.warning('Could not add ZCTextIndex to bika_setup_catalog')
            pass

        at = getToolByName(portal, 'archetype_tool')
        at.setCatalogsByType('Department',
                             ['bika_setup_catalog', "portal_catalog", ])
        at.setCatalogsByType('Container', ['bika_setup_catalog', ])
        at.setCatalogsByType('ContainerType', ['bika_setup_catalog', ])
        at.setCatalogsByType('AnalysisCategory', ['bika_setup_catalog', ])
        at.setCatalogsByType('AnalysisService',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('AnalysisSpec', ['bika_setup_catalog', ])
        at.setCatalogsByType('SampleCondition', ['bika_setup_catalog'])
        at.setCatalogsByType('SampleMatrix', ['bika_setup_catalog', ])
        at.setCatalogsByType('SampleType',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('SamplePoint',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('StorageLocation',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('SamplingDeviation', ['bika_setup_catalog', ])
        at.setCatalogsByType('IdentifierType', ['bika_setup_catalog', ])
        at.setCatalogsByType('Instrument',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('InstrumentType',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('InstrumentLocation',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('Method', ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('Multifile', ['bika_setup_catalog'])
        at.setCatalogsByType('AttachmentType', ['bika_setup_catalog', ])
        at.setCatalogsByType('Attachment', ['portal_catalog'])
        at.setCatalogsByType('Calculation',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('AnalysisProfile',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('ARTemplate',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('LabProduct',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('LabContact',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('Manufacturer',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('Preservation', ['bika_setup_catalog', ])
        at.setCatalogsByType('ReferenceDefinition',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('SRTemplate',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('SubGroup', ['bika_setup_catalog', ])
        at.setCatalogsByType('Supplier',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('Unit', ['bika_setup_catalog', ])
        at.setCatalogsByType('WorksheetTemplate',
                             ['bika_setup_catalog', 'portal_catalog'])
        at.setCatalogsByType('BatchLabel', ['bika_setup_catalog', ])

        addIndex(bsc, 'path', 'ExtendedPathIndex', 'getPhysicalPath')
        addIndex(bsc, 'allowedRolesAndUsers', 'KeywordIndex')
        addIndex(bsc, 'UID', 'FieldIndex')
        addIndex(bsc, 'SearchableText', 'ZCTextIndex', zc_extras)
        addIndex(bsc, 'Title', 'ZCTextIndex', zc_extras)
        addIndex(bsc, 'Description', 'ZCTextIndex', zc_extras)
        addIndex(bsc, 'id', 'FieldIndex')
        addIndex(bsc, 'getId', 'FieldIndex')
        addIndex(bsc, 'Type', 'FieldIndex')
        addIndex(bsc, 'portal_type', 'FieldIndex')
        addIndex(bsc, 'created', 'DateIndex')
        addIndex(bsc, 'Creator', 'FieldIndex')
        addIndex(bsc, 'getObjPositionInParent', 'GopipIndex')
        addIndex(bc, 'Identifiers', 'KeywordIndex')

        addIndex(bsc, 'title', 'FieldIndex', 'Title')
        addIndex(bsc, 'sortable_title', 'FieldIndex')
        addIndex(bsc, 'description', 'FieldIndex', 'Description')

        addIndex(bsc, 'review_state', 'FieldIndex')
        addIndex(bsc, 'inactive_state', 'FieldIndex')
        addIndex(bsc, 'cancellation_state', 'FieldIndex')

        addIndex(bsc, 'getAccredited', 'FieldIndex')
        addIndex(bsc, 'getAnalyst', 'FieldIndex')
        addIndex(bsc, 'getBlank', 'FieldIndex')
        addIndex(bsc, 'getCalculationTitle', 'FieldIndex')
        addIndex(bsc, 'getCalculationUID', 'FieldIndex')
        addIndex(bsc, 'getCalibrationExpiryDate', 'FieldIndex')
        addIndex(bsc, 'getCategoryTitle', 'FieldIndex')
        addIndex(bsc, 'getCategoryUID', 'FieldIndex')
        addIndex(bsc, 'getClientUID', 'FieldIndex')
        addIndex(bsc, 'getDepartmentTitle', 'FieldIndex')
        addIndex(bsc, 'getDepartmentUID', 'FieldIndex')
        addIndex(bsc, 'getDocumentID', 'FieldIndex')
        addIndex(bsc, 'getDuplicateVariation', 'FieldIndex')
        addIndex(bsc, 'getFormula', 'FieldIndex')
        addIndex(bsc, 'getFullname', 'FieldIndex')
        addIndex(bsc, 'getHazardous', 'FieldIndex')
        addIndex(bsc, 'getInstrumentLocationName', 'FieldIndex')
        addIndex(bsc, 'getInstrumentTitle', 'FieldIndex')
        addIndex(bsc, 'getInstrumentType', 'FieldIndex')
        addIndex(bsc, 'getInstrumentTypeName', 'FieldIndex')
        addIndex(bsc, 'getKeyword', 'FieldIndex')
        addIndex(bsc, 'getManagerEmail', 'FieldIndex')
        addIndex(bsc, 'getManagerName', 'FieldIndex')
        addIndex(bsc, 'getManagerPhone', 'FieldIndex')
        addIndex(bsc, 'getMaxTimeAllowed', 'FieldIndex')
        addIndex(bsc, 'getMethodID', 'FieldIndex')
        addIndex(bsc, 'getAvailableMethodUIDs', 'KeywordIndex')
        addIndex(bsc, 'getModel', 'FieldIndex')
        addIndex(bsc, 'getName', 'FieldIndex')
        addIndex(bsc, 'getPointOfCapture', 'FieldIndex')
        addIndex(bsc, 'getPrice', 'FieldIndex')
        addIndex(bsc, 'getSamplePointTitle', 'KeywordIndex')
        addIndex(bsc, 'getSamplePointUID', 'FieldIndex')
        addIndex(bsc, 'getSampleTypeTitle', 'FieldIndex')
        addIndex(bsc, 'getSampleTypeTitles', 'KeywordIndex')
        addIndex(bsc, 'getSampleTypeUID', 'FieldIndex')
        addIndex(bsc, 'getServiceUID', 'FieldIndex')
        addIndex(bsc, 'getServiceUIDs', 'KeywordIndex')
        addIndex(bsc, 'getTotalPrice', 'FieldIndex')
        addIndex(bsc, 'getUnit', 'FieldIndex')
        addIndex(bsc, 'getVATAmount', 'FieldIndex')
        addIndex(bsc, 'getVolume', 'FieldIndex')

        addColumn(bsc, 'path')
        addColumn(bsc, 'UID')
        addColumn(bsc, 'id')
        addColumn(bsc, 'getId')
        addColumn(bsc, 'Type')
        addColumn(bsc, 'portal_type')
        addColumn(bsc, 'getObjPositionInParent')

        addColumn(bsc, 'Title')
        addColumn(bsc, 'Description')
        addColumn(bsc, 'title')
        addColumn(bsc, 'sortable_title')
        addColumn(bsc, 'description')

        addColumn(bsc, 'review_state')
        addColumn(bsc, 'inactive_state')
        addColumn(bsc, 'cancellation_state')

        addColumn(bsc, 'getAccredited')
        addColumn(bsc, 'getInstrumentType')
        addColumn(bsc, 'getInstrumentTypeName')
        addColumn(bsc, 'getInstrumentLocationName')
        addColumn(bsc, 'getBlank')
        addColumn(bsc, 'getCalculationTitle')
        addColumn(bsc, 'getCalculationUID')
        addColumn(bsc, 'getCalibrationExpiryDate')
        addColumn(bsc, 'getCategoryTitle')
        addColumn(bsc, 'getCategoryUID')
        addColumn(bsc, 'getClientUID')
        addColumn(bsc, 'getDepartmentTitle')
        addColumn(bsc, 'getDuplicateVariation')
        addColumn(bsc, 'getFormula')
        addColumn(bsc, 'getFullname')
        addColumn(bsc, 'getHazardous')
        addColumn(bsc, 'getInstrumentTitle')
        addColumn(bsc, 'getKeyword')
        addColumn(bsc, 'getManagerName')
        addColumn(bsc, 'getManagerPhone')
        addColumn(bsc, 'getManagerEmail')
        addColumn(bsc, 'getMaxTimeAllowed')
        addColumn(bsc, 'getModel')
        addColumn(bsc, 'getName')
        addColumn(bsc, 'getPointOfCapture')
        addColumn(bsc, 'getPrice')
        addColumn(bsc, 'getSamplePointTitle')
        addColumn(bsc, 'getSamplePointUID')
        addColumn(bsc, 'getSampleTypeTitle')
        addColumn(bsc, 'getSampleTypeUID')
        addColumn(bsc, 'getServiceUID')
        addColumn(bsc, 'getTotalPrice')
        addColumn(bsc, 'getUnit')
        addColumn(bsc, 'getVATAmount')
        addColumn(bsc, 'getVolume')

        # portal_catalog
        pc = getToolByName(portal, 'portal_catalog', None)
        if pc is None:
            logger.warning('Could not find the portal_catalog tool.')
            return
        addIndex(pc, 'Analyst', 'FieldIndex')
        addColumn(pc, 'Analyst')
        # TODO: Nmrl
        addColumn(pc, 'getProvince')
        addColumn(pc, 'getDistrict')

        # Setting up all LIMS catalogs defined in catalog folder
        setup_catalogs(portal, getCatalogDefinitions())

    def setupTopLevelFolders(self, context):
        workflow = getToolByName(context, "portal_workflow")
        obj_id = 'arimports'
        if obj_id in context.objectIds():
            obj = context._getOb(obj_id)
            # noinspection PyBroadException
            try:
                workflow.doActionFor(obj, "hide")
            except:
                pass
            obj.setLayout('@@arimports')
            alsoProvides(obj, IARImportFolder)
            alsoProvides(obj, IHaveNoBreadCrumbs)


def create_CAS_IdentifierType(portal):
    """LIMS-1391 The CAS Nr IdentifierType is normally created by
    setuphandlers during site initialisation.
    """
    bsc = getToolByName(portal, 'bika_setup_catalog', None)
    idtypes = bsc(portal_type='IdentifierType', title='CAS Nr')
    if not idtypes:
        folder = portal.bika_setup.bika_identifiertypes
        idtype = _createObjectByType('IdentifierType', folder, tmpID())
        idtype.processForm()
        idtype.edit(title='CAS Nr',
                    description='Chemical Abstracts Registry number',
                    portal_types=['Analysis Service'])


def setupVarious(context):
    """
    Final Bika import steps.
    """
    if context.readDataFile('bika.lims_various.txt') is None:
        return

    site = context.getSite()
    gen = BikaGenerator()
    gen.setupGroupsAndRoles(site)
    gen.setupPortalContent(site)
    gen.setupPermissions(site)
    gen.setupTopLevelFolders(site)
    gen.setupVersioning(site)
    gen.setupCatalogs(site)

    # Plone's jQuery gets clobbered when jsregistry is loaded.
    setup = site.portal_setup
    setup.runImportStepFromProfile(
        'profile-plone.app.jquery:default', 'jsregistry')
    # setup.runImportStepFromProfile('profile-plone.app.jquerytools:default',
    #  'jsregistry')

    create_CAS_IdentifierType(site)
