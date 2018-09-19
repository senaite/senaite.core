# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import time
import transaction

from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.DCWorkflow.Guard import Guard

version = '1.2.9'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF HERE --------
    migrate_attachment_report_options(portal)

    # Reindex object security for client contents (see #991)
    reindex_client_local_owner_permissions(portal)

    # Add "Create partition" transition
    add_create_partition_transition(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def reindex_client_local_owner_permissions(portal):
    """https://github.com/senaite/senaite.core/issues/957 Reindex bika_setup
    objects located in clients to give proper permissions to client contacts.
    """
    start = time.time()
    bsc = portal.bika_setup_catalog
    uids = [c.UID() for c in portal.clients.objectValues()]
    brains = bsc(getClientUID=uids)
    total = len(brains)
    for num, brain in enumerate(brains):
        ob = brain.getObject()
        logger.info("Reindexing permission for {}/{} ({})"
                    .format(num, total, ob.absolute_url()))
        ob.reindexObjectSecurity()
    end = time.time()
    logger.info("Fixing local owner role on client objects took {:.2f}s"
                .format(end-start))
    transaction.commit()

    
def migrate_attachment_report_options(portal):
    """Migrate Attachments with the report option "a" (attach in report)
       to the option to "i" (ignore in report)
    """
    attachments = api.search({"portal_type": "Attachment"})
    total = len(attachments)
    logger.info("Migrating 'Attach to Report' -> 'Ingore in Report' "
                "for %d attachments" % total)
    for num, attachment in enumerate(attachments):
        obj = api.get_object(attachment)

        if obj.getReportOption() in ["a", ""]:
            obj.setReportOption("i")
            obj.reindexObject()
            logger.info("Migrated Attachment %s" % obj.getTextTitle())


def add_create_partition_transition(portal):
    logger.info("Adding partitioning workflow")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("bika_ar_workflow")

    # Transition: create_partitions
    update_role_mappings = False
    transition_id = "create_partitions"
    if transition_id not in workflow.transitions:
        update_role_mappings = True
        workflow.transitions.addTransition(transition_id)
    transition = workflow.transitions.create_partitions
    transition.setProperties(
        title="Create partitions",
        new_state_id='sample_received',
        after_script_name='',
        actbox_name="Create partitions", )
    guard = transition.guard or Guard()
    guard_props = {'guard_permissions': 'BIKA: Edit Results',
                   'guard_roles': '',
                   'guard_expr': 'python:here.guard_handler("create_partitions")'}
    guard.changeFromProperties(guard_props)
    transition.guard = guard

    # Add the transition to "sample_received" state
    state = workflow.states.sample_received
    if transition_id not in state.transitions:
        update_role_mappings = True
        state.transitions += (transition_id, )

    if not update_role_mappings:
        return

    # Update role mappings if necessary. Analysis Requests transitioned beyond
    # sample_received state are omitted.
    states = ["sampled", "scheduled_sampling", "to_be_preserved",
              "to_be_sampled", "sample_due", "sample_received"]
    query = dict(portal_type="AnalysisRequest", states=states)
    ars = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    total = len(ars)
    for num, ar in enumerate(ars, start=1):
        workflow.updateRoleMappingsFor(api.get_object(ar))
        if num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}".format(num, total))
