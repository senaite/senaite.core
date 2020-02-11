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

import time

import traceback
import transaction
from bika.lims import api
from bika.lims import logger
from bika.lims.api.security import get_roles
from bika.lims.api.security import get_user
from bika.lims.api.snapshot import has_snapshots
from bika.lims.api.snapshot import supports_snapshots
from bika.lims.api.snapshot import take_snapshot
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.worksheet_catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.interfaces import IReceived
from bika.lims.interfaces import ISubmitted
from bika.lims.interfaces import IVerified
from bika.lims.setuphandlers import setup_auditlog_catalog
from bika.lims.subscribers.setup import update_worksheet_manage_permissions
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.workflow import get_review_history_statuses
from DateTime import DateTime
from zope.interface import alsoProvides
from Products.ZCatalog.ProgressHandler import ZLogHandler

version = "1.3.1"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

SKIP_TYPES_FOR_AUDIT_LOG = [
    "Sample",
    "SamplePartition",
    "ARReport",
    "Reference",
]


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------
    setup.runImportStepFromProfile(profile, "actions")
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "workflow")
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "toolset")
    setup.runImportStepFromProfile(profile, "content")
    setup.runImportStepFromProfile(profile, "controlpanel")

    # Remove alls Samples and Partition
    # https://github.com/senaite/senaite.core/pull/1359
    remove_samples_and_partitions(portal)

    # Convert inline images
    # https://github.com/senaite/senaite.core/issues/1333
    convert_inline_images_to_attachments(portal)

    # https://github.com/senaite/senaite.core/pull/1324
    # initialize auditlogging
    setup_auditlog_catalog(portal)
    init_auditlog(portal)
    remove_log_action(portal)

    # Mark objects based on the transitions performed to them
    # https://github.com/senaite/senaite.core/pull/1330
    mark_transitions_performed(portal)

    # Reindex sortable_title to make sorting case-insenstive
    # https://github.com/senaite/senaite.core/pull/1337
    reindex_sortable_title(portal)

    # Remove unnecessary indexes/metadata from worksheet catalog
    # https://github.com/senaite/senaite.core/pull/1362
    cleanup_worksheet_catalog(portal)

    # Apply permissions for Manage Worksheets
    # https://github.com/senaite/senaite.core/issues/1387
    update_worksheet_manage_permissions(api.get_setup())

    # Add getInternalUse metadata
    # https://github.com/senaite/senaite.core/pull/1391
    add_metadata(portal, CATALOG_ANALYSIS_REQUEST_LISTING, "getInternalUse")

    # Reindex getWorksheetUID from analysis catalog to ensure all analyses are
    # visible in Worksheet view
    # https://github.com/senaite/senaite.core/pull/1397
    reindex_getWorksheetUID(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_samples_and_partitions(portal):
    """Wipe out samples and their contained partitions

    N.B.: We do not use a catalog search here due to inconsistencies in the
          deletion process and leftover objects.
    """
    logger.info("Removing samples and partitions ...")
    num = 0
    clients = portal.clients.objectValues()

    for client in clients:
        cid = client.getId()
        logger.info("Deleting all samples of client {}...".format(cid))
        sids = client.objectIds(spec="Sample")
        for sid in sids:
            num += 1
            # bypass security checks
            try:
                client._delObject(sid)
                logger.info("#{}: Deleted sample '{}' of client '{}'"
                            .format(num, sid, cid))
            except:
                logger.error("Cannot delete sample '{}': {}"
                             .format(sid, traceback.format_exc()))
            if num % 1000 == 0:
                commit_transaction(portal)

    logger.info("Removed a total of {} samples, committing...".format(num))
    commit_transaction(portal)


def convert_inline_images_to_attachments(portal):
    """Convert base64 inline images to attachments
    """
    catalog = api.get_tool("uid_catalog")
    brains = catalog({"portal_type": "AnalysisRequest"})
    total = len(brains)
    logger.info("Checking result interpretations of {} samples "
                "for inline base64 images...".format(total))
    for num, brain in enumerate(brains):
        if num and num % 1000 == 0:
            transaction.commit()
            logger.info("{}/{} samples processed"
                        .format(num, total))
        obj = api.get_object(brain)
        # get/set the resultsinterpretations
        ri = obj.getResultsInterpretationDepts()
        obj.setResultsInterpretationDepts(ri)

    # Commit all changes
    transaction.commit()


def init_auditlog(portal):
    """Initialize the contents for the audit log
    """
    # reindex the auditlog folder to display the icon right in the setup
    portal.bika_setup.auditlog.reindexObject()

    # Initialize contents for audit logging
    start = time.time()
    uid_catalog = api.get_tool("uid_catalog")
    brains = uid_catalog()
    total = len(brains)

    logger.info("Initializing {} objects for the audit trail...".format(total))
    for num, brain in enumerate(brains):
        # Progress notification
        if num and num % 1000 == 0:
            transaction.commit()
            logger.info("{}/{} ojects initialized for audit logging"
                        .format(num, total))
        # End progress notification
        if num + 1 == total:
            end = time.time()
            duration = float(end-start)
            logger.info("{} ojects initialized for audit logging in {:.2f}s"
                        .format(total, duration))

        if api.get_portal_type(brain) in SKIP_TYPES_FOR_AUDIT_LOG:
            continue

        obj = api.get_object(brain)

        if not supports_snapshots(obj):
            continue

        if has_snapshots(obj):
            continue

        # Take one snapshot per review history item
        rh = api.get_review_history(obj, rev=False)
        for item in rh:
            actor = item.get("actor")
            user = get_user(actor)
            if user:
                # remember the roles of the actor
                item["roles"] = get_roles(user)
            # The review history contains the variable "time" which we will set
            # as the "modification" time
            timestamp = item.pop("time", DateTime())
            item["time"] = timestamp.ISO()
            item["modified"] = timestamp.ISO()
            item["remote_address"] = None
            take_snapshot(obj, **item)


def remove_log_action(portal):
    """Removes the old Log action from types
    """
    logger.info("Removing Log Tab ...")
    portal_types = api.get_tool("portal_types")
    for name in portal_types.listContentTypes():
        ti = portal_types[name]
        actions = map(lambda action: action.id, ti._actions)
        for index, action in enumerate(actions):
            if action == "log":
                logger.info("Removing Log Action for {}".format(name))
                ti.deleteActions([index])
                break
    logger.info("Removing Log Tab [DONE]")


def mark_transitions_performed(portal):
    """Applies the IReceived, ISubmitted and IVerified interfaces to objects
    """
    mark_analysis_requests_transitions(portal)
    mark_analyses_transitions(portal)


def mark_analysis_requests_transitions(portal):
    logger.info("Marking Samples with IReceived and IVerified ...")
    statuses = [
        "sample_received",
        "attachment_due",
        "to_be_verified",
        "verified",
        "published",
        "invalid",
        "rejected",
        "cancelled", ]
    query = dict(review_state=statuses)
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Marking Samples with IReceived and IVerified: {}/{}"
                        .format(num, total))

        ar = api.get_object(brain)
        if brain.review_state in ["rejected", "cancelled"]:
            # There is no choice for "rejected" and "cancelled". We need to
            # look to the review_history
            prev_statuses = get_review_history_statuses(ar)
            if "received" in prev_statuses:
                alsoProvides(ar, IReceived)
            if "verified" in prev_statuses:
                alsoProvides(ar, IVerified)
        else:
            alsoProvides(ar, IReceived)

            if brain.review_state in ["verified", "published", "invalid"]:
                alsoProvides(ar, IVerified)

        if num % 1000 == 0 and num > 0:
            commit_transaction(portal)


def mark_analyses_transitions(portal):
    logger.info("Marking Analyses with ISubmitted and IVerified ...")
    statuses = ["to_be_verified", "verified", "published"]
    query = dict(review_state=statuses)
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Marking Analyses with ISubmitted and IVerified: {}/{}"
                        .format(num, total))

        an = api.get_object(brain)
        alsoProvides(an, ISubmitted)
        if brain.review_state in ["verified", "published"]:
            alsoProvides(an, IVerified)

        if num % 1000 == 0 and num > 0:
            commit_transaction(portal)


def commit_transaction(portal):
    start = time.time()
    logger.info("Commit transaction ...")
    transaction.commit()
    end = time.time()
    logger.info("Commit transaction ... Took {:.2f}s [DONE]"
                .format(end - start))


def reindex_sortable_title(portal):
    """Reindex sortable_title from some catalogs
    """
    catalogs = [
        "bika_catalog",
        "bika_setup_catalog",
        "portal_catalog",
    ]
    for catalog_name in catalogs:
        logger.info("Reindexing sortable_title for {} ...".format(catalog_name))
        handler = ZLogHandler(steps=100)
        catalog = api.get_tool(catalog_name)
        catalog.reindexIndex("sortable_title", None, pghandler=handler)
        commit_transaction(portal)


def cleanup_worksheet_catalog(portal):
    """Removes stale indexes and metadata from worksheet_catalog.
    """
    cat_id = CATALOG_WORKSHEET_LISTING
    logger.info("Cleaning up indexes and metadata from {} ...".format(cat_id))
    indexes_to_remove = [
    ]
    metadata_to_remove = [
        "getLayout",
    ]
    for index in indexes_to_remove:
        del_index(portal, cat_id, index)

    for metadata in metadata_to_remove:
        del_metadata(portal, cat_id, metadata)
    commit_transaction(portal)


def del_index(portal, catalog_id, index_name):
    logger.info("Removing '{}' index from '{}' ..."
                .format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name not in catalog.indexes():
        logger.info("Index '{}' not in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.delIndex(index_name)
    logger.info("Removing old index '{}' ...".format(index_name))


def add_metadata(portal, catalog_id, column, refresh_catalog=False):
    logger.info("Adding '{}' metadata to '{}' ...".format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column in catalog.schema():
        logger.info("Metadata '{}' already in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.addColumn(column)

    if refresh_catalog:
        logger.info("Refreshing catalog '{}' ...".format(catalog_id))
        handler = ZLogHandler(steps=100)
        catalog.refreshCatalog(pghandler=handler)

def del_metadata(portal, catalog_id, column, refresh_catalog=False):
    logger.info("Removing '{}' metadata from '{}' ..."
                .format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column not in catalog.schema():
        logger.info("Metadata '{}' not in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.delColumn(column)

    if refresh_catalog:
        logger.info("Refreshing catalog '{}' ...".format(catalog_id))
        handler = ZLogHandler(steps=100)
        catalog.refreshCatalog(pghandler=handler)


def reindex_getWorksheetUID(portal):
    """Reindex getWorksheetUID index from analysis_catalog
    """
    catalog_name = CATALOG_ANALYSIS_LISTING
    logger.info("Reindexing getWorksheetUID for {} ...".format(catalog_name))
    handler = ZLogHandler(steps=100)
    catalog = api.get_tool(catalog_name)
    catalog.reindexIndex("getWorksheetUID", None, pghandler=handler)
    commit_transaction(portal)
