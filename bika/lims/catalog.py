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
    Setup the catalogs given. Redefines the map between content types and
    catalogs and then checks the indexes and metacolumns, if one index/column
    doesn't exist in the catalog_definition any more in a catalog it will be
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
    archetype_tool = getToolByName(context, 'archetype_tool')
    # Mapping content types in catalogs
    to_reindex = _map_content_types(archetype_tool, catalogs_definition)
    # Merging the two lists and adding the new catalogs to reindex
    clean_and_rebuild = clean_and_rebuild +\
        list(set(to_reindex) - set(clean_and_rebuild))
    # Indexing
    for cat_id in catalogs_definition.keys():
        reindex = False
        reindex = _setup_catalog(
            archetype_tool, cat_id, catalogs_definition.get(cat_id, {}))
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
    ct_map = {}
    to_reindex = []
    # getting the dictionary of mapped content_types in the catalog
    map_types = archetype_tool.catalog_map
    for key in catalogs_definition.keys():
        # Mapping the catalog with the defined types
        types = catalog_info.get('types', [])
        for t in types:
            ct_map[t] = ct_map.get(t, []).append(key)
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
            # Adding to reindex
            to_reindex = to_reindex + catalogs_list + list(set2 - set1)
    return to_reindex


def _setup_catalog(archetype_tool, catalog_id, catalog_definition):
    """
    Given a catalog definition it updates the indexes, columns and content_type
    definitions of the catalog.
    :archetype_tool: an archetype_tool object
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
    catalog_info = catalog_definition.get(catalog_id, {})
    catalog = getToolByName(portal, catalog_id, None)
    if catalog is None:
        logger.warning('Could not find the %s tool.' % (catalog_id))
        return False
    # Indexes
    for idx in catalog_info.get('indexes', {}).keys():
        indexed = _addIndex(catalog, idx, catalog_info['indexes'][idx])
        reindex = True if indexed and not reindex else reindex
    # Columns
    for col in catalog_info.get('columns', {}).keys():
        created = _addColumn(catalog, col)
        reindex = True if indexed and not created else reindex
    return reindex


def _addIndex(catalog, index, indextype):
    if index not in catalog.indexes():
        try:
            catalog.addIndex(index, indextype)
            logger.info('Catalog index %s added.' % index)
        except:
            logger.error('Catalog index %s error while adding.' % index)


def _addColumn(cat, col):
    try:
        cat.addColumn(col)
        logger.info('Column %s added.' % col)
    except:
        logger.error('Catalog column %s error while adding.' % col)


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
        except:
            logger.error("Unable to clean and rebuild %s " % cat)
