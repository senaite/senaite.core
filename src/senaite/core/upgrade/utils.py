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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
import logging
import time
from contextlib import contextmanager

from pkg_resources import parse_version

import transaction
from Acquisition import aq_base
from bika.lims import api
from bika.lims.api import safe_unicode as u
from bika.lims.interfaces import IAuditable
from Persistence import PersistentMapping
from plone.dexterity.fti import DexterityFTI
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import get_installer
from Products.ZCatalog.ProgressHandler import ZLogHandler
from OFS.Image import File as OFSFile
from OFS.Image import Image as OFSImage
from plone.app.blob.field import BlobWrapper
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from senaite.core import logger
from senaite.core.api.catalog import add_zc_text_index
from senaite.core.interfaces.catalog import ISenaiteCatalogObject
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


def permanently_allow_type_for(portal_type, allowed_type):
    """Permanently allow to the type to be created below the obj
    """
    pt = api.get_tool("portal_types")
    fti = pt.get(portal_type)
    # get the current allowed types for the object
    allowed_types = fti.allowed_content_types
    # append the allowed type
    fti.allowed_content_types = allowed_types + (allowed_type, )


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


def copy_dates(src, target):
    """copy modification/creation date
    """
    created = api.get_creation_date(src)
    modified = api.get_modification_date(src)
    target.creation_date = created
    target.setModificationDate(modified)


def copy_creators(src, target):
    """Copy creators
    """
    target.setCreators(src.listCreators())


def copyPermMap(old):
    """bullet proof copy
    """
    new = PersistentMapping()
    for k, v in old.items():
        new[k] = v
    return new


def copy_workflow_history(src, target):
    """Copy workflow history
    """
    wfh = getattr(src, "workflow_history", None)
    if wfh:
        wfh = copyPermMap(wfh)
        target.workflow_history = wfh


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
    api.delete(obj, check_permissions=False, suppress_events=True)


def iter_senaite_catalogs():
    """Yield every catalog tool in the portal that is a SENAITE catalog
    """
    portal = api.get_portal()
    for obj in portal.objectValues():
        if ISenaiteCatalogObject.providedBy(obj):
            yield obj


def rebuild_index(catalog, index_name, clear=True):
    """Reindex every cataloged object on an index, optionally clearing first

    When `clear` is True (default) the index BTree is wiped before
    reindexing so stale keys from previous indexers are dropped --
    needed e.g. when an indexer changes its return type and existing
    keys would otherwise collide with the new ones (byte vs unicode).
    Set `clear=False` to keep existing keys and only refresh entries
    per docid via `reindexIndex`.

    Streams progress to the log via a `ZLogHandler` so long-running
    reindexes give feedback every 100 objects instead of going silent
    until the whole catalog is done.

    :param catalog: ZCatalog tool
    :param index_name: Index id
    :param clear: Clear the index BTree before reindexing
    :type clear: bool
    """
    if catalog is None:
        return
    if index_name not in catalog.indexes():
        logger.info(
            "Skipping %s on %s (index not found)" % (
                index_name, catalog.id))
        return
    index = catalog._catalog.getIndex(index_name)
    if index is None:
        return
    total = len(catalog)
    if clear:
        logger.info(
            "Clearing %s index on %s (%s objects to reindex) ..." % (
                index_name, catalog.id, total))
        index.clear()
    else:
        logger.info(
            "Reindexing %s on %s (%s objects) ..." % (
                index_name, catalog.id, total))
    pghandler = ZLogHandler(steps=100)
    catalog.reindexIndex(index_name, None, pghandler=pghandler)
    logger.info(
        "Rebuilt %s index on %s (%s objects)" % (
            index_name, catalog.id, total))


def uncatalog_brain(brain):
    """Uncatalog a stale catalog entry
    """
    if not api.is_brain(brain):
        return False
    catalog = brain.aq_parent
    path = api.get_path(brain)
    logger.warn(80*"*")
    logger.warn("Removing stale catalog brain from catalog %s on path %s"
                % (catalog.getId(), path))
    logger.warn(80*"*")
    catalog.uncatalog_object(path)
    return True


def remove_at_portal_types(tool, types_to_remove=[]):
    """Remove obsolete AT portal type information
    """

    if not types_to_remove:
        logger.warn("no AT types to remove from portal_types tool ...")
        return

    logger.info("Remove AT types from portal_types tool ...")
    pt = api.get_tool("portal_types")
    for type_name in types_to_remove:
        fti = pt.getTypeInfo(type_name)
        # keep DX FTIs
        if isinstance(fti, DexterityFTI):
            logger.info("Type '{}' is already a DX FTI".format(fti))
            continue
        elif not fti:
            # Removed already
            continue
        pt.manage_delObjects(fti.getId())

    # remove from AT's factory tool as well. This is necessary for the AT's
    # factory_tool to not shortcut `createObject?type_name=` on object creation
    ft = api.get_tool("portal_factory")
    at_types = ft.getFactoryTypes().keys()
    at_types = filter(lambda name: name not in types_to_remove, at_types)
    ft.manage_setPortalFactoryTypes(listOfTypeIds=at_types)

    logger.info("Remove AT types from portal_types tool ... [DONE]")


def blob_to_named_file(blob, default_filename=u"file"):
    """Convert an AT file/image value to a Dexterity NamedBlobFile/Image.

    Accepts:
    * A ``plone.app.blob.field.BlobWrapper`` (blob-aware AT fields).
    * An ``OFS.Image.Image`` / ``OFS.Image.File`` (the value stored
      by plain Archetypes ``ImageField`` / ``FileField``).

    Anything else falsy returns ``None``. Anything else truthy is
    returned unchanged, so legacy callers that already pass
    ``NamedBlobFile``/``NamedBlobImage`` instances keep working.
    """
    if not blob:
        return None

    if isinstance(blob, BlobWrapper):
        filename = u(blob.getFilename() or default_filename)
        content_type = blob.getContentType() or ""
        data = blob.data
    elif isinstance(blob, (OFSImage, OFSFile)):
        # ``filename`` attribute is set on upload but may be empty;
        # fall back to the persistent id, then the default.
        filename = u(getattr(blob, "filename", None)
                     or blob.getId()
                     or default_filename)
        content_type = blob.getContentType() or ""
        data = bytes(blob.data) if blob.data is not None else b""
    else:
        # Unknown shape (e.g. already a NamedBlobFile from a partial
        # earlier migration); leave it for the field setter to deal
        # with.
        return blob

    if content_type.startswith("image/"):
        return NamedBlobImage(
            data=data,
            filename=filename,
            contentType=content_type,
        )
    return NamedBlobFile(
        data=data,
        filename=filename,
        contentType=content_type,
    )
