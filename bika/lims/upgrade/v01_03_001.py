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
from bika.lims import logger
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.interfaces import IReceived, IVerified, ISubmitted
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims import api
from zope.interface import alsoProvides
from bika.lims.workflow import get_review_history_statuses

version = '1.3.1'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)


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
    setup.runImportStepFromProfile(profile, 'workflow')

    # Mark objects based on the transitions performed to them
    # https://github.com/senaite/senaite.core/pull/1330
    mark_transitions_performed(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


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
        "cancelled",]
    query = dict(review_state=statuses)
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Marking Samples with IReceived and IVerified: {}/{}"
                        .format(num, total))

        ar = api.get_object(brain)
        if brain.review_state in ["rejected", "cancelled"]:
            # There is no choice for "rejected" and "cancelled". We need to look
            # to the review_history
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
