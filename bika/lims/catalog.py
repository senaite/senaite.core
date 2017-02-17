# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.ZCatalog.ZCatalog import ZCatalog
from bika.lims.interfaces import IBikaCatalog
from bika.lims.interfaces import IBikaAnalysisCatalog
from bika.lims.interfaces import IBikaSetupCatalog
from bika.lims.interfaces import IBikaCatalogAnalysisRequestListing
from bika.lims import logger
import sys
import traceback
import copy
from zope.interface import implements
import transaction


# Using a variable to avoid plain strings in code
CATALOG_ANALYSIS_REQUEST_LISTING = 'bika_catalog_analysisrequest_listing'

_catalogs_definition = {
    # This catalog contains the metacolumns to list patients in bikalisting
    CATALOG_ANALYSIS_REQUEST_LISTING: {
        'types':   ['AnalysisRequest', ],
        'indexes': {
            # Minimum indexes for bika_listing
            # TODO: Can be removed?
            'id': 'FieldIndex',
            'getId': 'FieldIndex',
            'created': 'DateIndex',
            'Creator': 'FieldIndex',
            # TODO: Can be removed? Same as id
            'sortable_title': 'FieldIndex',
            # TODO-catalog: can be removed?
            'portal_type': 'FieldIndex',
            'UID': 'FieldIndex',
            'getClientUID': 'FieldIndex',
            'getSampleUID': 'FieldIndex',
            # Index that should be reindexed after some object modifications
            'review_state': 'FieldIndex',
            'cancellation_state': 'FieldIndex',
            'getBatchUID': 'FieldIndex',
            'getDateSampled': 'DateIndex',
            'getSamplingDate': 'DateIndex',
            'getDateReceived': 'DateIndex',
            'getDateVerified': 'DateIndex',
            'getDatePublished': 'DateIndex',
            'getSampler': 'FieldIndex',
            'getReceivedBy': 'FieldIndex',
            'getDepartmentUIDs': 'KeywordIndex',
        },
        'columns': [
            'UID',
            'getId',
            'Title',
            'created',
            'Creator',
            'getCreatorFullName',
            'getCreatorEmail',
            'review_state',
            'getObjectWorkflowStates',
            'getPhysicalPath',
            'getSampleUID',
            # Used to print the ID of the Sample in lists
            'getSampleID',
            # Used to create add an anchor to Sample ID that redirects to
            # the Sample view.
            'getSampleURL',
            'getClientOrderNumber',
            'getClientReference',
            'getClientSampleID',
            'getSampler',
            'getSamplerFullName',
            'getSamplerEmail',
            'getBatchUID',
            #  Used to print the ID of the Batch in lists
            'getBatchID',
            'getBatchURL',
            'getClientUID',
            'getClientTitle',
            'getClientURL',
            'getContactUID',
            'getContactUsername',
            'getContactEmail',
            'getContactURL',
            'getContactFullName',
            'getSampleTypeUID',
            'getSampleTypeTitle',
            'getSamplePointUID',
            'getSamplePointTitle',
            'getStorageLocationUID',
            'getStorageLocationTitle',
            'getPriority',
            'getSamplingDate',
            'getDateSampled',
            'getDateReceived',
            'getDateVerified',
            'getDatePublished',
            'getProfilesUID',
            'getProfilesURL',
            'getProfilesTitle',
            'getProfilesTitleStr',
            'getTemplateUID',
            'getTemplateURL',
            'getTemplateTitle',
            'getAnalysesNum',
            'getPrinted',
            'getSamplingDeviationTitle',
            # TODO: This should be updated through a clock
            'getLate',
            'getInvoiceExclude',
            'getHazardous',
            'getSamplingWorkflowEnabled',
            'getDepartmentUIDs',
        ]
    }
}


def getCatalogDefinitions():
    """
    Returns a dictionary with catalog definitions
    """
    return _catalogs_definition


def getCatalog(instance, field='UID'):
    """ Return the catalog which indexes objects of instance's type.
    If an object is indexed by more than one catalog, the first match
    will be returned.
    """
    uid = instance.UID()
    if 'workflow_skiplist' in instance.REQUEST and \
        [x for x in instance.REQUEST['workflow_skiplist']
         if x.find(uid) > -1]:
        return None
    else:
        # grab the first catalog we are indexed in.
        # we're only indexed in one.
        at = getToolByName(instance, 'archetype_tool')
        plone = instance.portal_url.getPortalObject()
        catalog_name = instance.portal_type in at.catalog_map \
            and at.catalog_map[instance.portal_type][0] or 'portal_catalog'
        catalog = getToolByName(plone, catalog_name)
        return catalog


class BikaCatalog(CatalogTool):

    """Catalog for various transactional types"""

    implements(IBikaCatalog)

    security = ClassSecurityInfo()
    _properties = ({'id': 'title', 'type': 'string', 'mode': 'w'},)

    title = 'Bika Catalog'
    id = 'bika_catalog'
    portal_type = meta_type = 'BikaCatalog'
    plone_tool = 1

    def __init__(self):
        ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')

    def clearFindAndRebuild(self):
        """
        """

        def indexObject(obj, path):
            self.reindexObject(obj)
        logger.info('Cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]

            self.manage_catalogClear()
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal.ZopeFindAndApply(portal,
                                    obj_metatypes=types,
                                    search_sub=True,
                                    apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaCatalog)


class BikaAnalysisCatalog(CatalogTool):

    """Catalog for analysis types"""

    implements(IBikaAnalysisCatalog)

    security = ClassSecurityInfo()
    _properties = ({'id': 'title', 'type': 'string', 'mode': 'w'},)

    title = 'Bika Analysis Catalog'
    id = 'bika_analysis_catalog'
    portal_type = meta_type = 'BikaAnalysisCatalog'
    plone_tool = 1

    def __init__(self):
        ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')

    def clearFindAndRebuild(self):
        """
        """

        def indexObject(obj, path):
            self.reindexObject(obj)
        logger.info('Cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]

            self.manage_catalogClear()
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal.ZopeFindAndApply(portal,
                                    obj_metatypes=types,
                                    search_sub=True,
                                    apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaAnalysisCatalog)


class BikaSetupCatalog(CatalogTool):

    """Catalog for all bika_setup objects"""

    implements(IBikaSetupCatalog)

    security = ClassSecurityInfo()
    _properties = ({'id': 'title', 'type': 'string', 'mode': 'w'},)

    title = 'Bika Setup Catalog'
    id = 'bika_setup_catalog'
    portal_type = meta_type = 'BikaSetupCatalog'
    plone_tool = 1

    def __init__(self):
        ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')

    def clearFindAndRebuild(self):
        """
        """

        def indexObject(obj, path):
            self.reindexObject(obj)
        logger.info('Cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]

            self.manage_catalogClear()
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal.ZopeFindAndApply(portal,
                                    obj_metatypes=types,
                                    search_sub=True,
                                    apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaSetupCatalog)


class BikaCatalogAnalysisRequestListing(CatalogTool):
    """
    Catalog to list analysis requests in BikaListing
    """
    implements(IBikaCatalogAnalysisRequestListing)
    title = 'Bika Catalog Analysis Request Listing'
    id = CATALOG_ANALYSIS_REQUEST_LISTING
    portal_type = meta_type = 'BikaCatalogAnalysisRequestListing'
    plone_tool = 1
    security = ClassSecurityInfo()
    _properties = (
      {'id': 'title', 'type': 'string', 'mode': 'w'},)

    def __init__(self):
        ZCatalog.__init__(self, self.id)

    security.declareProtected(ManagePortal, 'clearFindAndRebuild')

    def clearFindAndRebuild(self):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with an indexObject method), and reindexes them.
           This may take a long time.
        """
        def indexObject(obj, path):
            self.reindexObject(obj)
            transaction.commit()
        logger.info('Cleaning and rebuilding %s...' % self.id)
        try:
            at = getToolByName(self, 'archetype_tool')
            types = [k for k, v in at.catalog_map.items()
                     if self.id in v]
            self.manage_catalogClear()
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal.ZopeFindAndApply(
                portal,
                obj_metatypes=types,
                search_sub=True,
                apply_func=indexObject)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (self.id, e))
        logger.info('%s cleaned and rebuilt' % self.id)


InitializeClass(BikaCatalogAnalysisRequestListing)


def setup_catalogs(
        portal, catalogs_definition={},
        force_reindex=False, catalog_extensions={}):
    """
    Setup the given catalogs. Redefines the map between content types and
    catalogs and then checks the indexes and metacolumns, if one index/column
    doesn't exist in the catalog_definition any more it will be
    removed, otherwise, if a new index/column is found, it will be created.
    :portal: the Plone portal
    :catalogs_definition: a dictionary like
        {
            CATALOG_ID: {
                'types':   ['ContentType', ...],
                'indexes': {
                    'UID': 'FieldIndex',
                    ...
                },
                'columns': [
                    'Title',
                    ...
                ]
            }
        }
    :force_reindex: boolean to reindex the catalogs even if there is no need
        to do so.
    :catalog_extensions: a list of dictionaris with more elements to add to the
        ones defined in catalogs_definition. This variable should be used to
        add more columns in a catalog from another addon of bika.
        {
            'types': ['ContentType', ],
            'indexes': {
                'getDoctorUID': 'FieldIndex',
                ...
            },
            'columns': [
                'AnotherTitle',
                ...
            ]
        }
    """
    # If not given catalogs_definition, use the LIMS one
    if not catalogs_definition:
        catalogs_definition = getCatalogDefinitions()
    archetype_tool = getToolByName(portal, 'archetype_tool')
    # Making a copy of catalogs_definition and adding the catalog extensions
    # if required
    catalogs_definition_extended_copy = {}
    if catalog_extensions:
        catalogs_definition_extended_copy = _merge_both_catalogs(
            getCatalogDefinitions(), catalog_extensions)
    # Merging the extended catalogs definition with the catalogs definition
    catalogs_definition_copy = _merge_both_catalogs(
        catalogs_definition_extended_copy, catalogs_definition)
    # Mapping content types in catalogs
    # This variable will be used to clean reindex the catalog. Saves the
    # catalogs ids
    clean_and_rebuild = _map_content_types(
        archetype_tool, catalogs_definition_copy)
    # Indexing
    for cat_id in catalogs_definition_copy.keys():
        reindex = False
        reindex = _setup_catalog(
            portal, cat_id, catalogs_definition_copy.get(cat_id, {}))
        if (reindex or force_reindex) and (cat_id not in clean_and_rebuild):
            # add the catalog if it has not been added before
            clean_and_rebuild.append(cat_id)
    # Reindex the catalogs which needs it
    _cleanAndRebuildIfNeeded(portal, clean_and_rebuild)


def _merge_both_catalogs(catalogs_definition, catalog_extensions):
    """
    Merges two dictionaries and returns a new one with the merge of both
    :catalogs_definition: a dictionary like
        {
            CATALOG_ID: {
                'types':   ['ContentType', ...],
                'indexes': {
                    'UID': 'FieldIndex',
                    ...
                },
                'columns': [
                    'Title',
                    ...
                ]
            }
        }
    :catalog_extensions: the catalog to merge into catalogs_definition
        {
            CATALOG_ID: {
                'types':   ['ContentType', ...],
                'indexes': {
                    'UID': 'FieldIndex',
                    ...
                },
                'columns': [
                    'Title',
                    ...
                ]
            }
        }
    :return: a merge of the dictionaries from above with the same format.
    """

    result_dict = copy.deepcopy(catalogs_definition)
    ext_cat_ids = catalog_extensions.keys()
    if ext_cat_ids:
        original_dict_keys = result_dict.keys()
        for ext_cat_id in ext_cat_ids:
            if ext_cat_id in original_dict_keys:
                try:
                    # If catalog id is found in the original catalog
                    # definition, add the extension info to it
                    # Getting the types to add
                    ext_cat_types_info =\
                        catalog_extensions[ext_cat_id].get('types', [])
                    # Getting the indexes to add
                    ext_cat_indexes_info = \
                        catalog_extensions[ext_cat_id].get('indexes', {})
                    # Getting the columns to add
                    ext_cat_columns_info =\
                        catalog_extensions[ext_cat_id].get('columns', [])
                    # Adding the types
                    l_types = result_dict[ext_cat_id].get('types', [])
                    l_types += ext_cat_types_info
                    result_dict[ext_cat_id]['types'] = l_types
                    # Adding the indexes
                    d_idx = result_dict[ext_cat_id].get('indexes', {})
                    d_idx.update(ext_cat_indexes_info)
                    result_dict[ext_cat_id]['indexes'] = d_idx
                    # Adding the columns
                    l_cols = result_dict[ext_cat_id].get('columns', [])
                    l_cols += ext_cat_columns_info
                    result_dict[ext_cat_id]['columns'] = l_cols
                except:
                    logger.error(
                        'An error occured while updating the catalog %s due '
                        'to the following errot:' % ext_cat_id)
                    logger.error(traceback.format_exc())
            else:
                # If catalog id is not found in the original catalog
                # definition, definition, rise an info and create the new dict
                logger.info(
                    "Catalog %s doesn't exist in Bika LIMS catalog "
                    "definitions dictionary. A new catalog definition"
                    " might be created." % ext_cat_id)
                result_dict[ext_cat_id] = catalog_extensions[ext_cat_id]
    return result_dict


def _map_content_types(archetype_tool, catalogs_definition):
    """
    Updates the mapping for content_types against catalogs
    :archetype_tool: an archetype_tool object
    :catalogs_definition: a dictionary like
        {
            CATALOG_ID: {
                'types':   ['ContentType', ...],
                'indexes': {
                    'UID': 'FieldIndex',
                    ...
                },
                'columns': [
                    'Title',
                    ...
                ]
            }
        }
    """
    # This will be a dictionari like {'content_type':['catalog_id', ...]}
    ct_map = {}
    # This list will contain the atalog ids to be rebuild
    to_reindex = []
    # getting the dictionary of mapped content_types in the catalog
    map_types = archetype_tool.catalog_map
    for catalog_id in catalogs_definition.keys():
        catalog_info = catalogs_definition.get(catalog_id, {})
        # Mapping the catalog with the defined types
        types = catalog_info.get('types', [])
        for t in types:
            tmp_l = ct_map.get(t, [])
            tmp_l.append(catalog_id)
            ct_map[t] = tmp_l
    # Mapping
    for t in ct_map.keys():
        catalogs_list = ct_map[t]
        # Getting the previus mapping
        perv_catalogs_list = archetype_tool.catalog_map.get(t, [])
        # If the mapping has changed, update it
        set1 = set(catalogs_list)
        set2 = set(perv_catalogs_list)
        if set1 != set2:
            archetype_tool.setCatalogsByType(t, catalogs_list)
            # Adding to reindex only the catalogs that have changed
            to_reindex = to_reindex + list(set1 - set2) + list(set2 - set1)
    return to_reindex


def _setup_catalog(portal, catalog_id, catalog_definition):
    """
    Given a catalog definition it updates the indexes, columns and content_type
    definitions of the catalog.
    :portal: the Plone site object
    :catalog_id: a string as the catalog id
    :catalog_definition: a dictionary like
        {
            'types':   ['ContentType', ...],
            'indexes': {
                'UID': 'FieldIndex',
                ...
            },
            'columns': [
                'Title',
                ...
            ]
        }
    """

    reindex = False
    catalog = getToolByName(portal, catalog_id, None)
    if catalog is None:
        logger.warning('Could not find the %s tool.' % (catalog_id))
        return False
    # Indexes
    indexes_ids = catalog_definition.get('indexes', {}).keys()
    # Indexing
    for idx in indexes_ids:
        # The function returns if the index needs to be reindexed
        indexed = _addIndex(catalog, idx, catalog_definition['indexes'][idx])
        reindex = True if indexed else reindex
    # Removing indexes
    in_catalog_idxs = catalog.indexes()
    to_remove = list(set(in_catalog_idxs)-set(indexes_ids))
    for idx in to_remove:
        # The function returns if the index has been deleted
        desindexed = _delIndex(catalog, idx)
        reindex = True if desindexed else reindex
    # Columns
    columns_ids = catalog_definition.get('columns', [])
    for col in columns_ids:
        created = _addColumn(catalog, col)
        reindex = True if created else reindex
    # Removing columns
    in_catalog_cols = catalog.schema()
    to_remove = list(set(in_catalog_cols)-set(columns_ids))
    for col in to_remove:
        # The function returns if the index has been deleted
        desindexed = _delColumn(catalog, col)
        reindex = True if desindexed else reindex
    return reindex


def _addIndex(catalog, index, indextype):
    """
    This function indexes the index element into the catalog if it isn't yet.
    :catalog: a catalog object
    :index: an index id as string
    :indextype: the type of the index as string
    :return: a boolean as True if the element has been indexed and it returns
    False otherwise.
    """
    if index not in catalog.indexes():
        try:
            catalog.addIndex(index, indextype)
            logger.info('Catalog index %s added to %s.' % (index, catalog.id))
            return True
        except:
            logger.error(
                'Catalog index %s error while adding to %s.'
                % (index, catalog.id))
    return False


def _addColumn(cat, col):
    """
    This function adds a metadata column to the acatalog.
    :cat: a catalog object
    :col: a column id as string
    :return: a boolean as True if the element has been added and
        False otherwise
    """
    # First check if the metadata column already exists
    if col not in cat.schema():
        try:
            cat.addColumn(col)
            logger.info('Column %s added to %s.' % (col, cat.id))
            return True
        except:
            logger.error(
                'Catalog column %s error while adding to %s.' % (col, cat.id))
    return False


def _delIndex(catalog, index):
    """
    This function desindexes the index element from the catalog.
    :catalog: a catalog object
    :index: an index id as string
    :return: a boolean as True if the element has been desindexed and it
    returns False otherwise.
    """
    if index in catalog.indexes():
        try:
            catalog.delIndex(index)
            logger.info(
                'Catalog index %s deleted from %s.' % (index, catalog.id))
            return True
        except:
            logger.error(
                'Catalog index %s error while deleting from %s.'
                % (index, catalog.id))
    return False


def _delColumn(cat, col):
    """
    This function deletes a metadata column of the acatalog.
    :cat: a catalog object
    :col: a column id as string
    :return: a boolean as True if the element has been removed and
        False otherwise
    """
    # First check if the metadata column already exists
    if col in cat.schema():
        try:
            cat.delColumn(col)
            logger.info('Column %s deleted from %s.' % (col, cat.id))
            return True
        except:
            logger.error(
                'Catalog column %s error while deleting from %s.'
                % (col, cat.id))
    return False


def _cleanAndRebuildIfNeeded(portal, cleanrebuild):
    """
    Rebuild the given catalogs.
    :portal: the Plone portal object
    :cleanrebuild: a list with catalog ids
    """
    for cat in cleanrebuild:
        catalog = getToolByName(portal, cat)
        if catalog:
            catalog.clearFindAndRebuild()
        else:
            logger.warning('%s do not found' % cat)
