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

import transaction
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.DCWorkflow.Guard import Guard

version = '1.2.9'  # Remember version number in metadata.xml and setup.py
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

    # -------- ADD YOUR STUFF HERE --------

    # Display supplier view instead of reference samples per default
    # https://github.com/senaite/senaite.core/pull/1037
    setup.runImportStepFromProfile(profile, 'typeinfo')

    # Delete orphaned Attachments
    # https://github.com/senaite/senaite.core/issues/1025
    delete_orphaned_attachments(portal)

    # Migrate report option from attach (a) -> ignore (i)
    # https://github.com/senaite/senaite.core/pull/992
    migrate_attachment_report_options(portal)

    # Reindex object security for client contents
    # https://github.com/senaite/senaite.core/pull/991
    reindex_client_local_owner_permissions(portal)

    # Rename "retract_ar" transition to "invalidate"
    # https://github.com/senaite/senaite.core/pull/1027
    rename_retract_ar_transition(portal)

    # Rebind ARs that were generated because of the invalidation of other ARs
    # https://github.com/senaite/senaite.core/pull/1027
    rebind_invalidated_ars(portal)

    # Reindex Turnaround time and due date related fields
    # https://github.com/senaite/senaite.core/pull/1032
    recatalog_analyses_due_date(portal)

    # Update workflow states and permissions for AR/Sample rejection
    # https://github.com/senaite/senaite.core/pull/1041
    update_rejection_permissions(portal)

    # Remove getLate and add getDueDate metadata in ar_catalog
    # https://github.com/senaite/senaite.core/pull/1051
    update_analaysisrequests_due_date(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def delete_orphaned_attachments(portal):
    """Delete attachments where the Analysis was removed
       https://github.com/senaite/senaite.core/issues/1025
    """
    attachments = api.search({"portal_type": "Attachment"})
    total = len(attachments)
    logger.info("Integrity checking %d attachments" % total)
    for num, attachment in enumerate(attachments):
        obj = api.get_object(attachment)
        # The method `getRequest` from the attachment tries to get the AR
        # either directly or from one of the linked Analyses. If it returns
        # `None`, we can be sure that the attachment is neither assigned
        # directly to an AR nor to an Analysis.
        ar = obj.getRequest()
        if ar is None:
            obj_id = api.get_id(obj)
            api.get_parent(obj).manage_delObjects(obj_id)
            logger.info("Deleted orphaned Attachment {}".format(obj_id))


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


def rename_retract_ar_transition(portal):
    """Renames retract_ar transition to invalidate
    """
    logger.info("Renaming 'retract_ar' transition to 'invalidate'")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("bika_ar_workflow")

    if "invalidate" not in workflow.transitions:
        workflow.transitions.addTransition("invalidate")
    transition = workflow.transitions.invalidate
    transition.setProperties(
        title="Invalidate",
        new_state_id="invalid",
        after_script_name="",
        actbox_name="Invalidate",
    )
    guard = transition.guard or Guard()
    guard_props = {"guard_permissions": "BIKA: Retract",
                   "guard_roles": "",
                   "guard_expr": "python:here.guard_cancelled_object()"}
    guard.changeFromProperties(guard_props)
    transition.guard = guard

    for state in workflow.states.values():
        if 'retract_ar' in state.transitions:
            trans = filter(lambda id: id != 'retract_ar', state.transitions)
            trans += ('invalidate', )
            state.transitions = trans

    if "retract_ar" in workflow.transitions:
        workflow.transitions.deleteTransitions(["retract_ar"])


def rebind_invalidated_ars(portal):
    """Rebind the ARs automatically generated because of the retraction of their
    parent to the new field 'Invalidated'. The field used until now
    'ParentAnalysisRequest' will be used for partitioning
    """
    logger.info("Rebinding retracted/invalidated ARs")

    # Walk through the Analysis Requests that were generated because of an
    # invalidation, get the source AR and rebind the fields
    relationship = "AnalysisRequestChildAnalysisRequest"
    ref_catalog = api.get_tool(REFERENCE_CATALOG)
    retests = ref_catalog(relationship=relationship)
    total = len(retests)
    to_remove = list()
    num = 0
    for num, relation in enumerate(retests, start=1):
        relation = relation.getObject()
        if not relation:
            continue
        retest = relation.getTargetObject()
        invalidated = relation.getSourceObject()
        retest.setInvalidated(invalidated)
        # Set ParentAnalysisRequest field to None, cause we will use this field
        # for storing Primary-Partitions relationship.
        retest.setParentAnalysisRequest(None)

        # Remove the relationship!
        to_remove.append((relation.aq_parent, relation.id))

        if num % 100 == 0:
            logger.info("Rebinding invalidated ARs: {0}/{1}"
                        .format(num, total))

    # Remove relationships
    for relation_to_remove in to_remove:
        folder = relation_to_remove[0]
        rel_id = relation_to_remove[1]
        folder.manage_delObjects([rel_id])

    logger.info("Rebound {} invalidated ARs".format(num))


def recatalog_analyses_due_date(portal):
    """Recatalog the index and metadata field 'getDueDate'
    """
    logger.info("Updating Analyses getDueDate")
    # No need to update those analyses that are verified or published. Only
    # those that are under work
    catalog = api.get_tool(CATALOG_ANALYSIS_LISTING)
    review_states = ["retracted", "sample_due", "attachment_due",
                     "sample_received", "to_be_verified"]
    query = dict(portal_type="Analysis", review_state=review_states)
    analyses = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(analyses)
    num = 0
    for num, analysis in enumerate(analyses, start=1):
        analysis = api.get_object(analysis)
        catalog.catalog_object(analysis, idxs=['getDueDate'])
        if num % 100 == 0:
            logger.info("Updating Analysis getDueDate: {0}/{1}"
                        .format(num, total))

    logger.info("{} Analyses updated".format(num))


def update_rejection_permissions(portal):
    """Adds the permission 'Reject Analysis Request' and update the permission
     mappings accordingly """
    updated = update_rejection_permissions_for(portal, "bika_ar_workflow",
                                               "Reject Analysis Request")
    if updated:
        brains = api.search(dict(portal_type="AnalysisRequest"),
                            CATALOG_ANALYSIS_REQUEST_LISTING)
        update_rolemappings_for(brains, "bika_ar_workflow")


    updated = update_rejection_permissions_for(portal, "bika_sample_workflow",
                                               "Reject Sample")
    if updated:
        brains = api.search(dict(portal_type="Sample"), "bika_catalog")
        update_rolemappings_for(brains, "bika_sample_workflow")


def update_rejection_permissions_for(portal, workflow_id, permission_id):
    logger.info("Updating rejection permissions for {}".format(workflow_id))
    all_roles = ["Manager", "LabManager", "LabClerk", "Client", "Owner"]
    roles_mapping = {
        "sample_registered": all_roles,
        "scheduled_sampling": all_roles,
        "to_be_sampled": all_roles,
        "sampled": all_roles,
        "to_be_preserved": all_roles,
        "sample_due": all_roles,
        "sample_received": ["Manager", "LabManager", "LabClerk"],
        "attachment_due": ["Manager", "LabManager"],
        "to_be_verified": ["Manager", "LabManager"],
        # Those that only apply to sample_workflow below
        "expired": ["Manager", "LabManager"],
        "disposed": ["Manager", "LabManager"],
    }
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(workflow_id)

    if "rejected" not in workflow.states:
        logger.warning("rejected state not found for workflow {} [SKIP]"
                       .format(workflow.id))
        return False

    if permission_id in workflow.permissions:
        logger.info("'{}' already in place. [SKIP]".format(permission_id))
        return False

    workflow.permissions += (permission_id,)
    for state_id, state in workflow.states.items():
        if "reject" not in state.transitions:
            continue
        if state_id not in roles_mapping:
            continue
        roles = roles_mapping[state_id]
        state.setPermission(permission_id, False, roles)

    if "reject" not in workflow.transitions:
        workflow.transitions.addTransition("reject")
        transition = workflow.transitions.reject
        transition.setProperties(
            title="Reject",
            new_state_id="rejected",
            actbox_name="Reject",
        )
    transition = workflow.transitions.reject
    guard = transition.guard or Guard()
    guard_props = {
        "guard_permissions": permission_id,
        "guard_roles": "",
        "guard_expr": "python:here.bika_setup.isRejectionWorkflowEnabled()"
    }
    guard.changeFromProperties(guard_props)
    transition.guard = guard
    return True

def update_rolemappings_for(brains, workflow_id):
    logger.info("Updating role mappings for '{}'".format(workflow_id))
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(workflow_id)
    total = len(brains)
    num = 0
    for num, brain in enumerate(brains, start=1):
        workflow.updateRoleMappingsFor(api.get_object(brain))
        if num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}"
                        .format(num, total))
    logger.info("{} objects updated".format(num))


def update_analaysisrequests_due_date(portal):
    """Removes the metadata getLate from ar-catalog and adds the column
    getDueDate"""
    logger.info("Updating getLate -> getDueDate metadata columns ...")
    catalog_objects = False
    catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    if "getLate" in catalog.schema():
        catalog.delColumn("getLate")

    if "getDueDate" in catalog.schema():
        logger.info("getDueDate column already in catalog [SKIP]")
    else:
        logger.info("Adding column 'getDueDate' to catalog '{}' ..."
                    .format(catalog.id))
        catalog.addColumn("getDueDate")
        catalog_objects = True

    if "getDueDate" in catalog.indexes():
        logger.info("getDueDate index already in catalog [SKIP]")
    else:
        logger.info("Adding index 'getDueDate' to catalog '{}'"
                    .format(catalog.id))
        catalog.addIndex("getDueDate", "DateIndex")
        if not catalog_objects:
            catalog.manage_reindexIndex("getDueDate")

    if catalog_objects:
        # Only recatalog the objects if the column getDueDate was not there
        num = 0
        query = dict(portal_type="AnalysisRequest")
        ar_brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
        total = len(ar_brains)
        for num, analysis_request in enumerate(ar_brains):
            analysis_request = api.get_object(analysis_request)
            analysis_request.reindexObject(idxs=['getDueDate'])
            if num % 100 == 0:
                logger.info("Updating Analysis Request getDueDate: {0}/{1}"
                            .format(num, total))
        logger.info("{} Analysis Requests updated".format(num))

    logger.info("Updating getLate -> getDueDate metadata columns [DONE]")
