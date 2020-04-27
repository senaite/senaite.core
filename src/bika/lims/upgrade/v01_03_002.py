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

import transaction
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.bika_catalog import BIKA_CATALOG
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

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

    # Allow to detach a partition from its primary sample (#1420)
    setup.runImportStepFromProfile(profile, "rolemap")

    # Mixed permissions for transitions in client workflow (#1419)
    # Allow to detach a partition from its primary sample (#1420)
    # Allow clients to create batches (#1450)
    # Allow unassign transition for cancelled/rejected/retracted analyses #1461
    setup.runImportStepFromProfile(profile, "workflow")

    # Allow to detach a partition from its primary sample (#1420)
    update_partitions_role_mappings(portal)

    # Remove Identifiers
    remove_identifiers(portal)

    # Unindex stale catalog brains from the auditlog_catalog
    # https://github.com/senaite/senaite.core/issues/1438
    unindex_orphaned_brains_in_auditlog_catalog(portal)

    # Allow clients to create batches (#1450)
    add_indexng3_to_bika_catalog(portal)
    update_batches_role_mappings(portal)
    move_batch_to_client(portal)

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


def add_indexng3_to_bika_catalog(portal):
    """Adds a TextIndexNG3 in bika_catalog
    """
    index_name = "listing_searchable_text"
    logger.info("Adding index {} in {} ...".format(index_name, BIKA_CATALOG))
    catalog = api.get_tool(BIKA_CATALOG)
    if index_name in catalog.indexes():
        logger.info("Index {} already in Catalog [SKIP]".format(index_name))
        return

    catalog.addIndex(index_name, "TextIndexNG3")

    logger.info("Indexing new index {} ...".format(index_name))
    catalog.manage_reindexIndex(index_name)
    logger.info("Indexing new index {} [DONE]".format(index_name))


def update_batches_role_mappings(portal):
    """Updates the role mappings for batches folder cause we've changed the
    workflow bound to this type and we've added permission to Delete Objects
    """
    logger.info("Updating role mappings of batches folder ...")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("senaite_batches_workflow")
    workflow.updateRoleMappingsFor(portal.batches)
    portal.batches.reindexObject()
    logger.info("Updating role mappings of batches folder [DONE]")


def move_batch_to_client(portal):
    """
    Moving each Batch inside BatchFolder to its Client if it belongs to a client.
    This makes permissions easier.
    """
    logger.info("Moving Batches under Clients...")
    batchfolder = portal.batches
    total = batchfolder.objectCount()
    for num, (b_id, batch) in enumerate(batchfolder.items()):
        if num and num % 100 == 0:
            logger.info("Moving Batches under Clients: {}/{}"
                        .format(num, total))
        client = batch.getField("Client").get(batch)
        if client:
            # Check if all samples inside this Batch belong to same client
            samples = batch.getAnalysisRequestsBrains()
            client_uids = map(lambda sample: sample.getClientUID, samples)
            client_uids = list(set(client_uids))
            if len(client_uids) > 1:
                # Samples from different clients!. Unset the client
                logger.warn("Batch with client assigned, but samples from "
                            "others. Unassigning client: {} ({})"
                            .format(b_id, api.get_title(client)))
                batch.setClient(None)
                batch.reindexObject()

            elif client_uids and client_uids[0] != api.get_uid(client):
                # Assigned client does not match with the ones from the samples
                logger.warn("Batch with client assigned that does not match "
                            "with the client from samples. Unassigning client: "
                            "{} ({})".format(b_id, api.get_title(client)))
                batch.setClient(None)
                batch.reindexObject()

            else:
                # Move batch inside the client
                cp = batchfolder.manage_cutObjects(b_id)
                client.manage_pasteObjects(cp)

    logger.info("Moving Batches under Clients [DONE]")


def remove_identifiers(portal):
    """Remove Identifiers from the portal
    """
    # 1. Remove the identifiers and identifier types
    logger.info("Removing identifiers ...")

    setup = portal.bika_setup
    try:
        # we use _delOb because manage_delObjects raises an unauthorized here
        it = setup["bika_identifiertypes"]
        for i in it.objectValues():
            i.unindexObject()
        it.unindexObject()
        setup._delOb("bika_identifiertypes")
    except KeyError:
        pass

    # 2. Remove controlpanel configlet
    cp = portal.portal_controlpanel
    cp.unregisterConfiglet("bika_identifiertypes")

    # 3. Remove catalog indexes
    for cat in ["portal_catalog", "bika_catalog", "bika_setup_catalog"]:
        tool = portal[cat]
        if "Identifiers" in tool.indexes():
            tool.manage_delIndex("Identifiers")

    # 4. Remove type registration
    pt = portal.portal_types
    for t in ["IdentifierType", "IdentifierTypes"]:
        if t in pt.objectIds():
            pt.manage_delObjects(t)

    logger.info("Removing identifiers [DONE]")
