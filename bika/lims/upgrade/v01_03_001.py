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
from bika.lims.config import PROJECTNAME as product
from bika.lims.interfaces import IAnalysis
from bika.lims.subscribers.auditlog import has_snapshots
from bika.lims.subscribers.auditlog import is_auditable
from bika.lims.subscribers.auditlog import take_snapshot
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from DateTime import DateTime

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

    # https://github.com/senaite/senaite.core/pull/1324
    # initialize the auditlog
    init_auditlog(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def init_auditlog(portal):
    """Initialize the contents for the audit log
    """
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

        # skip initial audit log for Analyses
        if IAnalysis.providedBy(obj):
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
