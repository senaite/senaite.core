# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.catalog import getCatalogDefinitions
from bika.lims.catalog import setup_catalogs
from bika.lims.config import *

GROUPS = {
    # Dictionary {group_name: [roles]}
    "Analysts": ["Analyst", ],
    "Clients": ["Client", ],
    "LabClerks": ["LabClerk",],
    # TODO Unbound LabManagers from Manager role
    "LabManagers": ["LabManager", "Manager", ],
    "Preservers": ["Perserver", ],
    "Publishers": ["Publisher", ],
    "Verifiers": ["Verifier", ],
    "Samplers": ["Sampler", ],
    "RegulatoryInspectors": ["RegulatoryInspector", ],
    "SamplingCoordinators": ["SamplingCoordinator", ],
}

NAV_BAR_ITEMS_TO_HIDE = (
    # List of items to hide from navigation bar
    "arimports",
    "pricelists",
    "supplyorders",
)

# noinspection PyClassHasNoInit
class Empty:
    pass


class BikaGenerator(object):
    def __init__(self):
        pass

    def setupPortalContent(self, portal):
        """ Setup Bika site structure """
        self.remove_default_content(portal)
        self.reindex_structure(portal)

        portal.bika_setup.laboratory.unmarkCreationFlag()
        portal.bika_setup.laboratory.reindexObject()

    def reindex_structure(self, portal):
        # index objects - importing through GenericSetup doesn't
        for obj_id in ('clients',
                       'batches',
                       'pricelists',
                       'bika_setup',
                       'methods',
                       'analysisrequests',
                       'referencesamples',
                       'supplyorders',
                       'worksheets',
                       'reports',
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

    def setupGroupsAndRoles(self, portal):
        # Create groups
        groups_ids = portal.portal_groups.listGroupIds()
        groups_ids = filter(lambda gr: gr not in groups_ids, GROUPS.keys())
        for group_id in groups_ids:
            portal.portal_groups.addGroup(group_id, title=group_id,
                                          roles=GROUPS[group_id])

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
        # TODO Remove in >v1.3.0
        at.setCatalogsByType('Sample', ['bika_catalog', 'portal_catalog'])
        # TODO Remove in >v1.3.0
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
        addIndex(bc, 'Identifiers', 'KeywordIndex')
        addIndex(bc, 'is_active', 'BooleanIndex')
        addIndex(bc, 'BatchDate', 'DateIndex')
        addIndex(bc, 'getClientTitle', 'FieldIndex')
        addIndex(bc, 'getClientUID', 'FieldIndex')
        addIndex(bc, 'getClientID', 'FieldIndex')
        addIndex(bc, 'getClientBatchID', 'FieldIndex')
        addIndex(bc, 'getDateReceived', 'DateIndex')
        addIndex(bc, 'getDateSampled', 'DateIndex')
        addIndex(bc, 'getDueDate', 'DateIndex')
        addIndex(bc, 'getExpiryDate', 'DateIndex')
        addIndex(bc, 'getReferenceDefinitionUID', 'FieldIndex')
        addIndex(bc, 'getSampleTypeTitle', 'FieldIndex')
        addIndex(bc, 'getSampleTypeUID', 'FieldIndex')

        # https://github.com/senaite/senaite.core/pull/1091
        addIndex(bc, 'getSupportedServices', 'KeywordIndex')
        addIndex(bc, 'getBlank', 'BooleanIndex')
        addIndex(bc, 'isValid', 'BooleanIndex')

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
        addColumn(bc, 'getClientTitle')
        addColumn(bc, 'getClientID')
        addColumn(bc, 'getClientBatchID')
        addColumn(bc, 'getSampleTypeTitle')
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
        addIndex(bsc, 'is_active', 'BooleanIndex')

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
    gen.setupCatalogs(site)

    # Hide navbar items no longer used
    # https://github.com/senaite/senaite.core/pull/1304
    hide_navbar_items(site)


def hide_navbar_items(portal):
    """Remove navbar items that are no longer used
    """
    logger.info("Removing items from navigation bar ...")

    # Get the list of object ids for portal
    object_ids = portal.objectIds()
    object_ids = filter(lambda id: id in object_ids, NAV_BAR_ITEMS_TO_HIDE)
    for object_id in object_ids:
        item = portal[object_id]
        item.setExcludeFromNav(True)
        item.reindexObject()
