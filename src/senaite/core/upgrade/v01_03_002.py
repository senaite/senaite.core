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

import transaction
from senaite.core import api
from senaite.core import logger
from senaite.core.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from senaite.core.config import PROJECTNAME as product
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils

version = "1.3.2"  # Remember version number in metadata.xml and setup.py
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

    setup.runImportStepFromProfile(profile, "skins")

    # Allow to detach a partition from its primary sample (#1420)
    setup.runImportStepFromProfile(profile, "rolemap")

    # Mixed permissions for transitions in client workflow (#1419)
    # Allow to detach a partition from its primary sample (#1420)
    setup.runImportStepFromProfile(profile, "workflow")

    # Allow to detach a partition from its primary sample (#1420)
    update_partitions_role_mappings(portal)

    # Unindex stale catalog brains from the auditlog_catalog
    # https://github.com/senaite/senaite.core/issues/1438
    unindex_orphaned_brains_in_auditlog_catalog(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def unindex_orphaned_brains_in_auditlog_catalog(portal):
    """Fetch deletable types from the auditlog_catalog and check if the objects
    still exist. If the checkd analysis brains are orphaned, e.g. moved to a
    partition, the brain will be unindexed.
    """
    orphaned = []
    types_to_check = ["Analysis", "Attachment"]
    ac = api.get_tool("auditlog_catalog")
    brains = ac({"portal_type": types_to_check})
    total = len(brains)

    logger.info("Checking %s brains in auditlog_catalog" % total)

    for num, brain in enumerate(brains):
        if num % 100 == 0:
            logger.info("Checked %s/%s brains in auditlog_catalog"
                        % (num, total))
        try:
            obj = brain.getObject()
            obj._p_deactivate()
        except AttributeError:
            orphaned.append(brain)

    if orphaned:
        logger.info("Unindexing %s orphaned brains in auditlog_catalog..."
                    % len(orphaned))

    for num, brain in enumerate(orphaned):
        logger.info("Unindexing %s/%s broken catalog brain"
                    % (num + 1, len(orphaned)))
        ac.uncatalog_object(brain.getPath())

    transaction.commit()


def update_partitions_role_mappings(portal):
    """Updates the rolemappings for existing partitions that are in a suitable
     state, so they can be detached from the primary sample they belong to
    """
    logger.info("Updating role mappings of partitions ...")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("bika_ar_workflow")

    # States that allow detach transition as defined in workflow definition in
    # order to query and update role mappings of objects that matter
    allowed_states = [
        "to_be_preserved", "sample_due", "sample_received", "to_be_verified",
        "verified"
    ]
    query = dict(portal_type="AnalysisRequest",
                 isRootAncestor=False,
                 review_state=allowed_states)

    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings of partitions: {}/{}"
                        .format(num, total))
        partition = api.get_object(brain)
        workflow.updateRoleMappingsFor(partition)
        partition.reindexObjectSecurity()

    logger.info("Updating role mappings of partitions [DONE]")
