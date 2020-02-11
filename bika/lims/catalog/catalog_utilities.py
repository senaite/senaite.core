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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import logger
from bika.lims.catalog.analysis_catalog import \
    bika_catalog_analysis_listing_definition
from bika.lims.catalog.analysisrequest_catalog import \
    bika_catalog_analysisrequest_listing_definition
from bika.lims.catalog.autoimportlogs_catalog import \
    bika_catalog_autoimportlogs_listing_definition
from bika.lims.catalog.report_catalog import bika_catalog_report_definition
from bika.lims.catalog.worksheet_catalog import \
    bika_catalog_worksheet_listing_definition
from Products.CMFCore.utils import getToolByName


def getCatalogDefinitions():
    """
    Returns a dictionary with catalogs definitions.
    """
    final = {}
    analysis_request = bika_catalog_analysisrequest_listing_definition
    analysis = bika_catalog_analysis_listing_definition
    autoimportlogs = bika_catalog_autoimportlogs_listing_definition
    worksheet = bika_catalog_worksheet_listing_definition
    report = bika_catalog_report_definition
    # Merging the catalogs
    final.update(analysis_request)
    final.update(analysis)
    final.update(autoimportlogs)
    final.update(worksheet)
    final.update(report)
    return final


def getCatalog(instance, field='UID'):
    """
    Returns the catalog that stores objects of instance passed in type.
    If an object is indexed by more than one catalog, the first match
    will be returned.

    :param instance: A single object
    :type instance: ATContentType
    :returns: The first catalog that stores the type of object passed in
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


def setup_catalogs(
        portal, catalogs_definition={},
        force_reindex=False, catalogs_extension={}, force_no_reindex=False):
    """
    Setup the given catalogs. Redefines the map between content types and
    catalogs and then checks the indexes and metacolumns, if one index/column
    doesn't exist in the catalog_definition any more it will be
    removed, otherwise, if a new index/column is found, it will be created.

    :param portal: The Plone's Portal object
    :param catalogs_definition: a dictionary with the following structure
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
    :type catalogs_definition: dict
    :param force_reindex: Force to reindex the catalogs even if there's no need
    :type force_reindex: bool
    :param force_no_reindex: Force reindexing NOT to happen.
    :param catalog_extensions: An extension for the primary catalogs definition
        Same dict structure as param catalogs_definition. Allows to add
        columns and indexes required by Bika-specific add-ons.
    :type catalog_extensions: dict
    """
    # If not given catalogs_definition, use the LIMS one
    if not catalogs_definition:
        catalogs_definition = getCatalogDefinitions()

    # Merge the catalogs definition of the extension with the primary
    # catalog definition
    definition = _merge_catalog_definitions(catalogs_definition,
                                            catalogs_extension)

    # Mapping content types in catalogs
    # This variable will be used to clean reindex the catalog. Saves the
    # catalogs ids
    archetype_tool = getToolByName(portal, 'archetype_tool')
    clean_and_rebuild = _map_content_types(archetype_tool, definition)

    # Indexing
    for cat_id in definition.keys():
        reindex = False
        reindex = _setup_catalog(
            portal, cat_id, definition.get(cat_id, {}))
        if (reindex or force_reindex) and (cat_id not in clean_and_rebuild):
            # add the catalog if it has not been added before
            clean_and_rebuild.append(cat_id)
    # Reindex the catalogs which needs it
    if not force_no_reindex:
        _cleanAndRebuildIfNeeded(portal, clean_and_rebuild)
    return clean_and_rebuild


def _merge_catalog_definitions(dict1, dict2):
    """
    Merges two dictionaries that represent catalogs definitions. The first
    dictionary contains the catalogs structure by default and the second dict
    contains additional information. Usually, the former is the Bika LIMS
    catalogs definition and the latter is the catalogs definition of an add-on
    The structure of each dict as follows:
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

    :param dict1: The dictionary to be used as the main template (defaults)
    :type dict1: dict
    :param dict2: The dictionary with additional information
    :type dict2: dict
    :returns: A merged dict with the same structure as the dicts passed in
    :rtype: dict
    """
    if not dict2:
        return dict1.copy()

    outdict = {}
    # Use dict1 as a template
    for k, v in dict1.items():
        if k not in dict2 and isinstance(v, dict):
            outdict[k] = v.copy()
            continue
        if k not in dict2 and isinstance(v, list):
            outdict[k] = v[:]
            continue
        if k == 'indexes':
            sdict1 = v.copy()
            sdict2 = dict2[k].copy()
            sdict1.update(sdict2)
            outdict[k] = sdict1
            continue
        if k in ['types', 'columns']:
            list1 = v
            list2 = dict2[k]
            outdict[k] = list(set(list1 + list2))
            continue
        if isinstance(v, dict):
            sdict1 = v.copy()
            sdict2 = dict2[k].copy()
            outdict[k] = _merge_catalog_definitions(sdict1, sdict2)

    # Now, add the rest of keys from dict2 that don't exist in dict1
    for k, v in dict2.items():
        if k in outdict:
            continue
        outdict[k] = v.copy()
    return outdict


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
    :returns: a boolean as True if the element has been indexed and it returns
    False otherwise.
    """
    if index not in catalog.indexes():
        try:
            if indextype == 'ZCTextIndex':
                addZCTextIndex(catalog, index)
            else:
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
    :returns: a boolean as True if the element has been added and
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
    :returns: a boolean as True if the element has been desindexed and it
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
    :returns: a boolean as True if the element has been removed and
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


def addZCTextIndex(catalog, index_name):

    if catalog is None:
        logger.warning('Could not find the catalog tool.' + catalog)
        return

    # Create lexicon to be able to add ZCTextIndex
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

    try:
        catalog.manage_addProduct['ZCTextIndex'].manage_addLexicon('Lexicon',
                                                               'Lexicon', elem)
    except:
        logger.warning('Could not add ZCTextIndex to '+str(catalog))

    catalog.addIndex(index_name, 'ZCTextIndex', zc_extras)


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
            logger.warning("Catalog '%s' not found" % cat)


class Empty:
    """
    Just a class to use when we need an object with some attributes to send to
    another objects an a parameter.
    """
    pass
