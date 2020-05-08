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

import logging
import time

import transaction
from Acquisition import aq_base
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.catalog_utilities import addZCTextIndex
from plone.app.blob.field import BlobWrapper
from plone.app.blob.interfaces import IBlobField
from Products.Archetypes.interfaces import ISchema
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.common import HAS_LINGUA_PLONE
from Products.contentmigration.migrator import BaseInlineMigrator
from Products.contentmigration.walker import CustomQueryWalker
from Products.ZCatalog.ProgressHandler import ZLogHandler
from transaction import savepoint

# Interesting page for logging indexing process and others:
# https://github.com/plone/Products.ZCatalog/tree/master/src/Products/ZCatalog
# and
# https://github.com/plone/Products.CMFPlone/blob/master/Products/CMFPlone
# /CatalogTool.py

LOG = logging.getLogger('contentmigration')


def migrate_to_blob(context, portal_type, query={}, remove_old_value=True):
    """Migrates FileFields fields to blob ones for a given portal_type.
    The wueries are done against 'portal_catalog', 'uid_catalog' and
    'reference_catalog'

    :param context: portal root object as context
    :param query: an expression to filter the catalog by other filters than
    the portal_type.
    :param portal_type: The portal type name the migration is migrating *from*
    """
    migrator = makeMigrator(
        context, portal_type, remove_old_value=remove_old_value)
    walker = BikaCustomQueryWalker(context, migrator, query=query)
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()


class BikaCustomQueryWalker(CustomQueryWalker):
    """Walker using portal_catalog and an optional custom query.
    This class overrides the original one in order to log and inform
    about the migration process.
    """
    additionalQuery = {}

    def walk(self):
        """
        Walks around and returns all objects which needs migration
        It does exactly the same as the original method, but add some
        progress loggers.

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: generator
        """
        catalog = self.catalog
        query = self.additionalQuery.copy()
        query['portal_type'] = self.src_portal_type
        query['meta_type'] = self.src_meta_type

        if HAS_LINGUA_PLONE and 'Language' in catalog.indexes():
            query['Language'] = 'all'

        brains = catalog(query)
        limit = getattr(self, 'limit', False)
        if limit:
            brains = brains[:limit]
        obj_num_total = len(brains)
        logger.info('{} {} objects will be migrated walking through {}'
                    .format(obj_num_total, self.src_portal_type, catalog.id))
        counter = 0
        for brain in brains:
            if counter % 100 == 0:
                logger.info('Progress: {} objects have been migrated out of {}'
                            .format(counter, obj_num_total))
            try:
                obj = brain.getObject()
            except AttributeError:
                LOG.error("Couldn't access %s" % brain.getPath())
                continue

            if self.callBefore is not None and callable(self.callBefore):
                if not self.callBefore(obj, **self.kwargs):
                    continue

            try:
                state = obj._p_changed
            except Exception:
                state = 0
            if obj is not None:
                yield obj
                # safe my butt
                if state is None:
                    obj._p_deactivate()
            counter += 1
            if obj_num_total == counter:
                logger.info(
                    'Progress: {} objects have been migrated out of {}'
                    .format(counter, obj_num_total))


# helper to build custom blob migrators for the given type. It is based on
# the function defined in plone/app/blob/migrations.py with the same name.
def makeMigrator(context, portal_type, remove_old_value=True):
    """ generate a migrator for the given at-based portal type """
    meta_type = portal_type

    class BlobMigrator(BaseInlineMigrator):
        """in-place migrator for archetypes based content that copies
        file/image data from old non-blob fields to new fields with the same
        name  provided by archetypes.schemaextender.

        see `plone3 to 4 migration guide`__

        .. __: https://plone.org/documentation/manual/upgrade-guide/version
        /upgrading-plone-3-x-to-4.0/updating-add-on-products-for-plone-4.0
        /use-plone.app.blob-based-blob-storage
        """

        src_portal_type = portal_type
        src_meta_type = meta_type
        dst_portal_type = portal_type
        dst_meta_type = meta_type
        fields = []

        def getFields(self, obj):
            if not self.fields:
                # get the blob fields to migrate from the first object
                for field in ISchema(obj).fields():
                    if IBlobField.providedBy(field):
                        self.fields.append(field.getName())
            return self.fields

        @property
        def fields_map(self):
            fields = self.getFields(None)
            return dict([(name, None) for name in fields])

        def migrate_data(self):
            fields = self.getFields(self.obj)
            for name in fields:
                # access old field by not using schemaextender
                oldfield = self.obj.schema[name]
                is_imagefield = False
                if hasattr(oldfield, 'removeScales'):
                    # clean up old image scales
                    is_imagefield = True
                    oldfield.removeScales(self.obj)
                value = oldfield.get(self.obj)

                if not value:
                    # no image/file data: don't copy it over to blob field
                    # this way it's save to run migration multiple times w/o
                    # overwriting existing data
                    continue

                if isinstance(aq_base(value), BlobWrapper):
                    # already a blob field, no need to migrate it
                    continue

                # access new field via schemaextender
                field = self.obj.getField(name)
                field.getMutator(self.obj)(value)

                if remove_old_value:
                    # Remove data from old field to not end up with data
                    # stored twice - in ZODB and blobstorage
                    if is_imagefield:
                        oldfield.set(self.obj, 'DELETE_IMAGE')
                    else:
                        oldfield.set(self.obj, 'DELETE_FILE')

        def last_migrate_reindex(self):
            # The original method checks the modification date in order to
            # keep the old one, but we don't care about it.
            self.obj.reindexObject()

    return BlobMigrator


class UpgradeUtils(object):
    def __init__(self, portal, pgthreshold=100):
        self.portal = portal
        self.reindexcatalog = {}
        self.refreshcatalog = []
        self.pgthreshold = pgthreshold

    def getInstalledVersion(self, product):
        qi = self.portal.portal_quickinstaller
        info = qi.upgradeInfo(product)
        return info['installedVersion']

    def isOlderVersion(self, product, version):
        # If the version to upgrade is lower than te actual version of the
        # product, skip the step to prevent out-of-date upgrade
        # Since there are heteregeneous names of versioning before v3.2.0, we
        # need to convert the version string to numbers, format and compare
        iver = self.getInstalledVersion(product)
        iver = self.normalizeVersion(iver)
        nver = self.normalizeVersion(version)
        logger.debug('{0} versions: Installed {1} - Target {2}'
                     .format(product, nver, iver))
        return nver < iver

    def normalizeVersion(self, version):
        ver = version.replace('.', '')
        major = ver[0] if len(ver) >= 1 else '0'
        minor = ver[1] if len(ver) >= 2 else '0'
        rev = ver[2:] if len(ver) >= 3 else '0'
        patch = 0
        if len(rev) == 5:
            patch = rev[1:]
            rev = rev[:1]
        elif len(rev) > 2:
            patch = rev[2:]
            rev = rev[:2]

        return '{0}.{1}.{2}.{3}'.format(
            '{:02d}'.format(int(major)),
            '{:02d}'.format(int(minor)),
            '{:02d}'.format(int(rev)),
            '{:04d}'.format(int(patch)))

    def delIndexAndColumn(self, catalog, index):
        self.delIndex(catalog, index)
        self.delColumn(catalog, index)

    def addIndexAndColumn(self, catalog, index, indextype):
        self.addIndex(catalog, index, indextype)
        self.addColumn(catalog, index)

    def reindexAndRefresh(self):
        self.refreshCatalogs()

    def _getCatalog(self, catalog):
        if isinstance(catalog, str):
            return getToolByName(self.portal, catalog)
        return catalog

    def delIndex(self, catalog, index):
        cat = self._getCatalog(catalog)
        if index not in cat.indexes():
            return
        cat.delIndex(index)
        logger.info('Deleted index {0} from catalog {1}'.format(
            index, cat.id))

    def delColumn(self, catalog, column):
        cat = self._getCatalog(catalog)
        if column not in cat.schema():
            return
        cat.delColumn(column)
        logger.info('Deleted column {0} from catalog {1} deleted.'.format(
            column, cat.id))

    def addIndex(self, catalog, index, indextype):
        cat = self._getCatalog(catalog)
        if index in cat.indexes():
            return
        if indextype == 'ZCTextIndex':
            addZCTextIndex(cat, index)
        else:
            cat.addIndex(index, indextype)
        logger.info('Catalog index %s added.' % index)
        indexes = self.reindexcatalog.get(cat.id, [])
        indexes.append(index)
        indexes = list(set(indexes))
        self.reindexcatalog[cat.id] = indexes
        transaction.commit()

    def addColumn(self, catalog, column):
        cat = self._getCatalog(catalog)
        if column in cat.schema():
            return
        cat.addColumn(column)
        logger.info('Added column {0} to catalog {1}'.format(
            column, cat.id))
        if cat.id not in self.refreshcatalog:
            logger.info("{} to refresh because col {} added".format(
                catalog, column
            ))
            self.refreshcatalog.append(cat.id)
        transaction.commit()

    def reindexIndex(self, catalog, index):
        cat = self._getCatalog(catalog)
        if index not in cat.indexes():
            logger.warn("Index {} not found in {}".format(index, catalog))
            return
        indexes = self.reindexcatalog.get(cat.id, [])
        if index not in indexes:
            indexes.append(index)
            self.reindexcatalog[cat.id] = indexes

    def refreshCatalogs(self):
        """
        It reindexes the modified catalogs but, while cleanAndRebuildCatalogs
        recatalogs all objects in the database, this method only reindexes over
        the already cataloged objects.

        If a metacolumn is added it refreshes the catalog, if only a new index
        is added, it reindexes only those new indexes.
        """
        to_refresh = self.refreshcatalog[:]
        to_reindex = self.reindexcatalog.keys()
        to_reindex = to_reindex[:]
        done = []
        # Start reindexing the catalogs with new columns
        for catalog_to_refresh in to_refresh:
            logger.info(
                'Catalog {0} refreshing started'.format(catalog_to_refresh))
            catalog = getToolByName(self.portal, catalog_to_refresh)
            handler = ZLogHandler(self.pgthreshold)
            catalog.refreshCatalog(pghandler=handler)
            logger.info('Catalog {0} refreshed'.format(catalog_to_refresh))
            transaction.commit()
            done.append(catalog_to_refresh)
        # Now the catalogs which only need reindxing
        for catalog_to_reindex in to_reindex:
            if catalog_to_reindex in done:
                continue
            logger.info(
                'Catalog {0} reindexing started'.format(catalog_to_reindex))
            catalog = getToolByName(
                self.portal, catalog_to_reindex)
            indexes = self.reindexcatalog[catalog_to_reindex]
            handler = ZLogHandler(self.pgthreshold)
            catalog.reindexIndex(indexes, None, pghandler=handler)
            logger.info('Catalog {0} reindexed'.format(catalog_to_reindex))
            transaction.commit()
            done.append(catalog_to_reindex)

    def cleanAndRebuildCatalog(self, catid):
        catalog = getToolByName(self.portal, catid)
        # manage_catalogRebuild does the same as clearFindAndRebuild
        # but it alse loggs cpu and time.
        catalog.manage_catalogRebuild()
        logger.info('Catalog {0} cleaned and rebuilt'.format(catid))
        transaction.commit()

    def cleanAndRebuildCatalogs(self):
        cats = self.refreshcatalog + self.reindexcatalog.keys()
        for catid in cats:
            self.cleanAndRebuildCatalog(catid)

    def recursiveUpdateRoleMappings(self, ob, wfs=None, commit_window=1000):
        """Code taken from Products.CMFPlone.WorkflowTool

        This version adds some commits and loggins
        """
        wf_tool = api.get_tool("portal_workflow")

        if wfs is None:
            wfs = {}
            for id in wf_tool.objectIds():
                wf = wf_tool.getWorkflowById(id)
                if hasattr(aq_base(wf), 'updateRoleMappingsFor'):
                    wfs[id] = wf

        # Returns a count of updated objects.
        count = 0
        wf_ids = wf_tool.getChainFor(ob)
        if wf_ids:
            changed = 0
            for wf_id in wf_ids:
                wf = wfs.get(wf_id, None)
                if wf is not None:
                    did = wf.updateRoleMappingsFor(ob)
                    if did:
                        changed = 1
            if changed:
                count = count + 1
                if hasattr(aq_base(ob), 'reindexObject'):
                    # Reindex security-related indexes
                    try:
                        ob.reindexObject(idxs=['allowedRolesAndUsers'])
                    except TypeError:
                        # Catch attempts to reindex portal_catalog.
                        pass
        if hasattr(aq_base(ob), 'objectItems'):
            obs = ob.objectItems()
            if obs:
                committed = 0
                logged = 0
                for k, v in obs:
                    if count - logged >= 100:
                        logger.info(
                            "Updating role mappings for {}: {}".format(
                                repr(ob), count))
                        logged += count

                    changed = getattr(v, '_p_changed', 0)
                    processed = self.recursiveUpdateRoleMappings(v, wfs,
                                                                 commit_window)
                    count += processed
                    if changed is None:
                        # Re-ghostify.
                        v._p_deactivate()

                    if count - committed >= commit_window:
                        commit_transaction()
                        committed += count
        return count


def commit_transaction():
    start = time.time()
    logger.info("Commit transaction ...")
    transaction.commit()
    end = time.time()
    logger.info("Commit transaction ... Took {:.2f}s [DONE]"
                .format(end - start))


def del_metadata(catalog_id, column):
    logger.info("Removing '{}' metadata from '{}' ..."
                .format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column not in catalog.schema():
        logger.info("Metadata '{}' not in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.delColumn(column)
