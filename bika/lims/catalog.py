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
from bika.lims import logger
import sys
import traceback
from zope.interface import implements


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

        at = getToolByName(self, 'archetype_tool')
        types = [k for k, v in at.catalog_map.items()
                 if self.id in v]

        self.manage_catalogClear()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal.ZopeFindAndApply(portal,
                                obj_metatypes=types,
                                search_sub=True,
                                apply_func=indexObject)

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

        at = getToolByName(self, 'archetype_tool')
        types = [k for k, v in at.catalog_map.items()
                 if self.id in v]

        self.manage_catalogClear()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal.ZopeFindAndApply(portal,
                                obj_metatypes=types,
                                search_sub=True,
                                apply_func=indexObject)

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

        at = getToolByName(self, 'archetype_tool')
        types = [k for k, v in at.catalog_map.items()
                 if self.id in v]

        self.manage_catalogClear()
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal.ZopeFindAndApply(portal,
                                obj_metatypes=types,
                                search_sub=True,
                                apply_func=indexObject)

InitializeClass(BikaSetupCatalog)


def setup_catalogs(portal, catalogs_definition):
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
    """
    # This variable will be used to clean reindex the catalog. Saves the
    # catalogs ids
    clean_and_rebuild = []
    archetype_tool = getToolByName(portal, 'archetype_tool')
    # Mapping content types in catalogs
    to_reindex = _map_content_types(archetype_tool, catalogs_definition)
    # Merging the two lists and adding the new catalogs to reindex
    clean_and_rebuild = clean_and_rebuild +\
        list(set(to_reindex) - set(clean_and_rebuild))
    # Indexing
    for cat_id in catalogs_definition.keys():
        reindex = False
        reindex = _setup_catalog(
            portal, cat_id, catalogs_definition.get(cat_id, {}))
        if reindex and cat_id not in clean_and_rebuild:
            # add the catalog if it has not been added before
            clean_and_rebuild.append(cat_id)
    # Reindex the catalogs which needs it
    _cleanAndRebuildIfNeeded(portal, clean_and_rebuild)


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
    to_reindex = []
    # getting the dictionary of mapped content_types in the catalog
    map_types = archetype_tool.catalog_map
    for catalog_id in catalogs_definition.keys():
        catalog_info = catalogs_definition.get(catalog_id, {})
        # Mapping the catalog with the defined types
        types = catalog_info.get('types', [])
        for t in types:
            l = ct_map.get(t, [])
            l.append(catalog_id)
            ct_map[t] = l
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
            # Adding to reindex only the catalogs that have differed
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
            catalog.delIndex(index, indextype)
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
        logger.info('Cleaning and rebuilding %s...' % cat)
        try:
            catalog = getToolByName(portal, cat)
            catalog.clearFindAndRebuild()
            logger.info('%s cleaned and rebuilt' % cat)
        except:
            logger.error(traceback.format_exc())
            e = sys.exc_info()
            logger.error(
                "Unable to clean and rebuild %s due to: %s" % (cat, e))
