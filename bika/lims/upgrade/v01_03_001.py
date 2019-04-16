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

import time

import transaction
from bika.lims import api
from bika.lims import logger
from bika.lims.api.security import get_roles
from bika.lims.api.security import get_user
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PROJECTNAME as product
# from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IReceived
from bika.lims.interfaces import ISubmitted
from bika.lims.interfaces import IVerified
from bika.lims.subscribers.auditlog import has_snapshots
from bika.lims.subscribers.auditlog import is_auditable
from bika.lims.catalog import setup_catalogs
from bika.lims.catalog.auditlog_catalog import catalog_auditlog_definition
from bika.lims.subscribers.auditlog import take_snapshot
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.workflow import get_review_history_statuses
from DateTime import DateTime
from zope.interface import alsoProvides

version = "1.3.1"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


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
    setup.runImportStepFromProfile(profile, "workflow")
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "toolset")
    setup.runImportStepFromProfile(profile, "content")

    # https://github.com/senaite/senaite.core/pull/1324
    # initialize auditlogging
    init_auditlog_catalog(portal)
    init_auditlog(portal)
    remove_log_action(portal)

    # Mark objects based on the transitions performed to them
    # https://github.com/senaite/senaite.core/pull/1330
    mark_transitions_performed(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def init_auditlog_catalog(portal):
    """Initialize the auditlog catalog
    """
    # setup the auditlog catalog
    logger.info("Setup Audit Log Catalog")
    setup_catalogs(portal, catalog_auditlog_definition)

    # XXX is there another way to do this?
    # Setup TXNG3 index
    catalog = portal.auditlog_catalog
    index = catalog.Indexes.get("listing_searchable_text")
    index.index.default_encoding = "utf-8"
    index.index.query_parser = "txng.parsers.en"
    index.index.autoexpand = "always"
    index.index.autoexpand_limit = 3
    index._p_changed = 1

    logger.info("Setup Audit Log Catalog [DONE]")


def init_auditlog(portal):
    """Initialize the contents for the audit log
    """
    # reindex the audit log controlpanel
    portal.bika_setup.auditlog.reindexObject()

    # Initialize contents for audit logging
    start = time.time()
    uid_catalog = api.get_tool("uid_catalog")
    brains = uid_catalog()
    total = len(brains)

    logger.info("Initializing {} objects for the audit trail...".format(total))
    for num, brain in enumerate(brains):
        # Progress notification
        if num % 1000 == 0:
            transaction.commit()
            logger.info("{}/{} ojects initialized for audit logging"
                        .format(num, total))
        # End progress notification
        if num + 1 == total:
            end = time.time()
            duration = float(end-start)
            logger.info("{} ojects initialized for audit logging in {:.2f}s"
                        .format(total, duration))

        obj = api.get_object(brain)

        if not is_auditable(obj):
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
