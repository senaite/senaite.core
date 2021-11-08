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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
import logging
import time
from contextlib import contextmanager

from pkg_resources import parse_version

import transaction
from Acquisition import aq_base
from Acquisition import aq_parent
from bika.lims import api
from bika.lims.interfaces import IAuditable
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import get_installer
from Products.ZCatalog.ProgressHandler import ZLogHandler
from senaite.core import logger
from senaite.core.api.catalog import add_zc_text_index
from zope.interface import alsoProvides
from zope.lifecycleevent import modified

# Interesting page for logging indexing process and others:
# https://github.com/plone/Products.ZCatalog/tree/master/src/Products/ZCatalog
# and
# https://github.com/plone/Products.CMFPlone/blob/master/Products/CMFPlone
# /CatalogTool.py

LOG = logging.getLogger("contentmigration")


class UpgradeUtils(object):
    def __init__(self, portal, pgthreshold=100):
        self.portal = portal
        self.reindexcatalog = {}
        self.refreshcatalog = []
        self.pgthreshold = pgthreshold

    def getInstalledVersion(self, product):
        qi = get_installer(self.portal)
        info = qi.upgrade_info(product)
        version = qi.get_product_version(product)
        return info.get("installedVersion", version)

    def isOlderVersion(self, product, version):
        # If the version to upgrade is lower than te actual version of the
        # product, skip the step to prevent out-of-date upgrade
        # Since there are heteregeneous names of versioning before v3.2.0, we
        # need to convert the version string to numbers, format and compare

        from_version = parse_version(self.getInstalledVersion(product))
        to_version = parse_version(version)
        return to_version < from_version

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
            add_zc_text_index(cat, index)
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


@contextmanager
def temporary_allow_type(obj, allowed_type):
    """Temporary allow content type creation in obj
    """
    pt = api.get_tool("portal_types")
    portal_type = api.get_portal_type(obj)
    fti = pt.get(portal_type)
    # get the current allowed types for the object
    allowed_types = fti.allowed_content_types
    # append the allowed type
    fti.allowed_content_types = allowed_types + (allowed_type, )

    yield obj

    # reset the allowed content types
    fti.allowed_content_types = allowed_types


def set_uid(obj, uid):
    """Set uid on dexterity object
    """
    if api.is_dexterity_content(obj):
        setattr(obj, "_plone.uuid", uid)
    elif api.is_at_content(obj):
        setattr(obj, "_at_uid", uid)
    else:
        raise TypeError("Cannot set UID on that object")
    modified(obj)


def copy_snapshots(src, target):
    """copy over snapshots from source -> target
    """
    snapshots = api.snapshot.get_snapshots(src)
    storage = api.snapshot.get_storage(target)
    storage[:] = map(json.dumps, snapshots)[:]
    alsoProvides(target, IAuditable)


def uncatalog_object(obj):
    """Uncatalog the object for all catalogs
    """
    # uncatalog from registered catalogs
    obj.unindexObject()
    # explicitly uncatalog from uid_catalog
    uid_catalog = api.get_tool("uid_catalog")
    url = "/".join(obj.getPhysicalPath()[2:])
    uid_catalog.uncatalog_object(url)


def catalog_object(obj):
    """Catalog the object
    """
    obj.reindexObject()


def delete_object(obj):
    """delete the object w/o firing events
    """
    uncatalog_object(obj)
    parent = aq_parent(obj)
    parent._delObject(obj.getId(), suppress_events=True)
