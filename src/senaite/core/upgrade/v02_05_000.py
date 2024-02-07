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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import transaction
from Acquisition import aq_base
from bika.lims import api
from bika.lims.api import security
from bika.lims.interfaces import IReceived
from bika.lims.utils import changeWorkflowState
from senaite.core import logger
from senaite.core.api.catalog import add_index
from senaite.core.api.catalog import del_column
from senaite.core.api.catalog import del_index
from senaite.core.api.catalog import reindex_index
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import CLIENT_CATALOG
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.catalog import REPORT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.config.registry import CLIENT_LANDING_PAGE
from senaite.core.permissions import ManageBika
from senaite.core.permissions import TransitionReceiveSample
from senaite.core.registry import get_registry_record
from senaite.core.registry import set_registry_record
from senaite.core.setuphandlers import _run_import_step
from senaite.core.setuphandlers import add_dexterity_items
from senaite.core.setuphandlers import CATALOG_MAPPINGS
from senaite.core.setuphandlers import setup_auditlog_catalog_mappings
from senaite.core.setuphandlers import setup_catalog_mappings
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.setuphandlers import setup_portal_catalog
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import uncatalog_brain
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.workflow import ANALYSIS_WORKFLOW
from senaite.core.workflow import SAMPLE_WORKFLOW
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility

PORTAL_CATALOG = "portal_catalog"

version = "2.5.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

CONTENT_ACTIONS = [
    # portal_type, action
    ("Client", {
        "id": "manage_access",
        "name": "Manage Access",
        "action": "string:${object_url}/@@sharing",
        # NOTE: We use this permission to hide the action from logged in client
        # contacts
        "permission": ManageBika,
        # "permission": "Sharing page: Delegate roles",
        "category": "object",
        "visible": True,
        "icon_expr": "",
        "link_target": "",
        "condition": "",
        "insert_after": "edit",
    }),
]


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

    # -------- ADD YOUR STUFF BELOW --------

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def rebuild_sample_zctext_index_and_lexicon(tool):
    """Recreate sample listing_searchable_text ZCText index and Lexicon
    """
    # remove the existing index
    index = "listing_searchable_text"
    del_index(SAMPLE_CATALOG, index)
    # remove the Lexicon
    catalog = api.get_tool(SAMPLE_CATALOG)
    if "Lexicon" in catalog.objectIds():
        catalog.manage_delObjects("Lexicon")
    # recreate the index + lexicon
    add_index(SAMPLE_CATALOG, index, "ZCTextIndex")
    # reindex
    reindex_index(SAMPLE_CATALOG, index)


@upgradestep(product, version)
def setup_labels(tool):
    """Setup labels for SENAITE
    """
    logger.info("Setup Labels")
    portal = api.get_portal()

    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    tool.runImportStepFromProfile(profile, "plone.app.registry")
    setup_core_catalogs(portal)

    items = [
        ("labels",
         "Labels",
         "Labels")
    ]
    setup = api.get_senaite_setup()
    add_dexterity_items(setup, items)


def drop_portal_catalog(tool):
    """Drop all indexing to portal_catalog
    """
    logger.info("Drop Portal Catalog ...")
    portal = api.get_portal()

    # setup core catalog mappings
    setup_catalog_mappings(portal)

    # cleanup portal_catalog indexes
    setup_portal_catalog(portal)

    for portal_type, catalogs in CATALOG_MAPPINGS:
        uncatalog_type(portal_type, catalog=PORTAL_CATALOG)

    logger.info("Drop Portal Catalog [DONE]")


def setup_client_catalog(tool):
    """Setup client catalog
    """
    logger.info("Setup Client Catalog ...")
    portal = api.get_portal()

    # setup and rebuild client_catalog
    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)
    client_catalog = api.get_tool(CLIENT_CATALOG)
    client_catalog.clearFindAndRebuild()

    # portal_catalog cleanup
    uncatalog_type("Client", catalog="portal_catalog")

    logger.info("Setup Client Catalog [DONE]")


def setup_contact_catalog(tool):
    """Setup contact catalog
    """
    logger.info("Setup Contact Catalog ...")
    portal = api.get_portal()

    # setup and rebuild client_catalog
    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)
    contact_catalog = api.get_tool(CONTACT_CATALOG)
    contact_catalog.clearFindAndRebuild()

    # portal_catalog cleanup
    uncatalog_type("Contact", catalog=PORTAL_CATALOG)
    uncatalog_type("LabContact", catalog=PORTAL_CATALOG)
    uncatalog_type("SupplierContact", catalog=PORTAL_CATALOG)

    # senaite_catalog_setup cleaup
    uncatalog_type("Contact", catalog=SETUP_CATALOG)
    uncatalog_type("LabContact", catalog=SETUP_CATALOG)
    uncatalog_type("SupplierContact", catalog=SETUP_CATALOG)

    logger.info("Setup Contact Catalog [DONE]")


def uncatalog_type(portal_type, catalog="portal_catalog", **kw):
    """Uncatalog all entries of the given type from the catalog
    """
    query = {"portal_type": portal_type}
    query.update(kw)
    brains = api.search(query, catalog=catalog)

    # NOTE: Catalog results are of type `ZTUtils.Lazy.LazyMap` and it might
    #       fail during iteration with the following traceback:
    #
    # Traceback (innermost last):
    #   Module ZPublisher.WSGIPublisher, line 176, in transaction_pubevents
    #   Module ZPublisher.WSGIPublisher, line 385, in publish_module
    #   Module ZPublisher.WSGIPublisher, line 288, in publish
    #   Module ZPublisher.mapply, line 85, in mapply
    #   Module ZPublisher.WSGIPublisher, line 63, in call_object
    #   Module Products.GenericSetup.tool, line 1135, in manage_doUpgrades
    #   Module Products.GenericSetup.upgrade, line 185, in doStep
    #   Module senaite.core.upgrade.v02_05_000, line 142, in drop_portal_catalog
    #   Module senaite.core.upgrade.v02_05_000, line 196, in uncatalog_type
    #   Module ZTUtils.Lazy, line 201, in __getitem__
    #   Module Products.ZCatalog.Catalog, line 131, in __getitem__
    # KeyError: -693164432
    #
    # Therefore, we convert the results first to a `list` to catch the error
    # inside the loop!
    for brain in list(brains):
        try:
            uncatalog_brain(brain)
        except KeyError:
            logger.error(
                "!!! Failed to uncatalog '%s' in catalog '%s' !!! "
                "Consider removing it manually." % (brain.getId, catalog))
            continue


def setup_catalogs(tool):
    """Setup all core catalogs and ensure all indexes are present
    """
    logger.info("Setup Catalogs ...")
    portal = api.get_portal()

    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)
    setup_auditlog_catalog_mappings(portal)

    logger.info("Setup Catalogs [DONE]")


def update_report_catalog(tool):
    """Update indexes in report catalog and add new metadata columns
    """
    logger.info("Update report catalog ...")
    portal = api.get_portal()

    # ensure new indexes are created
    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)

    # remove columns
    del_column(REPORT_CATALOG, "getClientTitlegetClientURL")
    del_column(REPORT_CATALOG, "getDatePrinted")

    logger.info("Update report catalog [DONE]")


@upgradestep(product, version)
def import_registry(tool):
    """Import registry step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, "plone.app.registry")


def create_client_groups(tool):
    """Create for all Clients an explicit Group
    """
    logger.info("Create client groups ...")
    clients = api.search({"portal_type": "Client"}, CLIENT_CATALOG)
    total = len(clients)
    for num, client in enumerate(clients):
        obj = api.get_object(client)
        logger.info("Processing client %s/%s: %s"
                    % (num+1, total, obj.getName()))

        # recreate the group
        obj.remove_group()

        # skip group creation
        if not get_registry_record("auto_create_client_group", True):
            logger.info("Auto group creation is disabled in registry. "
                        "Skipping group creation ...")
            continue

        group = obj.create_group()
        # add all linked client contacts to the group
        for contact in obj.getContacts():
            user = contact.getUser()
            if not user:
                continue
            logger.info("Adding user '%s' to the client group '%s'"
                        % (user.getId(), group.getId()))
            obj.add_user_to_group(user)

    logger.info("Create client groups [DONE]")


def reindex_client_security(tool):
    """Reindex client object security to grant the owner role for the client
       group to all contents
    """
    logger.info("Reindex client security ...")

    clients = api.search({"portal_type": "Client"}, CLIENT_CATALOG)
    total = len(clients)
    for num, client in enumerate(clients):
        obj = api.get_object(client)
        logger.info("Processing client %s/%s: %s"
                    % (num+1, total, obj.getName()))

        if not obj.get_group():
            logger.info("No client group exists for client %s. "
                        "Skipping reindexing ..." % obj.getName())
            continue

        _recursive_reindex_object_security(obj)

        logger.info("Commiting client %s/%s" % (num+1, total))
        transaction.commit()
        logger.info("Commit done")

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Reindex client security [DONE]")


def _recursive_reindex_object_security(obj):
    """Recursively reindex object security for the given object
    """
    if hasattr(aq_base(obj), "objectValues"):
        children = obj.objectValues()
        for num, child_obj in enumerate(children):
            if num and num % 100 == 0:
                path = api.get_path(obj)
                logger.info("{}: committing children {} ...".format(path, num))
                transaction.commit()
            _recursive_reindex_object_security(child_obj)

    # We don't do obj.reindexObject(idxs=["allowedRolesAndUsers"]) because
    # the function reindex the whole object (metadata included) if the catalog
    # does not contain the index 'allowedRolesAndUsers'. This makes the system
    # to consume a lot of RAM when thousands of objects need to be processed.
    # Also, the function does other stuff like refreshing Etag and so on, that
    # are things that we are not interested at all, actually. We just want the
    # index allowedRolesAndUsers to be updated, nothing else
    idx = "allowedRolesAndUsers"
    for cat in api.get_catalogs_for(obj):
        if idx not in cat.indexes():
            continue
        path = api.get_path(obj)
        cat.catalog_object(obj, path, idxs=[idx], update_metadata=0)

    obj._p_deactivate()


def add_content_actions(tool):
    logger.info("Add cotent actions ...")
    portal_types = api.get_tool("portal_types")
    for record in CONTENT_ACTIONS:
        portal_type, action = record
        type_info = portal_types.getTypeInfo(portal_type)
        action_id = action.get("id")
        # remove any previous added actions with the same ID
        _remove_action(type_info, action_id)
        # pop out the position info
        insert_after = action.pop("insert_after", None)
        # add the action
        type_info.addAction(**action)
        # sort the action to the right position
        actions = type_info._cloneActions()
        action_ids = map(lambda a: a.id, actions)
        if insert_after in action_ids:
            ref_index = action_ids.index(insert_after)
            index = action_ids.index(action_id)
            action = actions.pop(index)
            actions.insert(ref_index + 1, action)
            type_info._actions = tuple(actions)

        logger.info("Added action id '%s' to '%s'",
                    action_id, portal_type)
    logger.info("Add content actions [DONE]")


def _remove_action(type_info, action_id):
    """Removes the action id from the type passed in
    """
    actions = map(lambda action: action.id, type_info._actions)
    if action_id not in actions:
        return True
    index = actions.index(action_id)
    type_info.deleteActions([index])
    return _remove_action(type_info, action_id)


@upgradestep(product, version)
def import_workflow(tool):
    """Import workflow step from profiles

    NOTE: we use the upgradestep decorator, because workflows are modified by
          other add-ons quite often.
    """
    logger.info("Import Workflow ...")
    portal = tool.aq_inner.aq_parent
    _run_import_step(portal, "workflow", profile=profile)
    logger.info("Import Workflow [DONE]")


def update_workflow_mappings_analyses(tool):
    """Update the WF mappings for Analyses
    """
    logger.info("Updating role mappings for Analyses ...")
    wf_id = "senaite_analysis_workflow"
    query = {"portal_type": "Analysis"}
    brains = api.search(query, ANALYSIS_CATALOG)
    _update_workflow_mappings_for(wf_id, brains)
    logger.info("Updating role mappings for Analyses [DONE]")


def _update_workflow_mappings_for(wf_id, brains):
    """Helper to update role mappings for the given brains
    """
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}".format(num, total))
        if num and num % 1000 == 0:
            logger.info("Committing {0}/{1}".format(num, total))
            transaction.commit()
            logger.info("Committed {0}/{1}".format(num, total))
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=["allowedRolesAndUsers"])
        # free memory
        obj._p_deactivate()


def remove_legacy_reports(tool):
    """Removes legacy Report folder and contents
    """
    logger.info("Removing legacy reports ...")

    # remove the reports folder, along with its contents
    portal = tool.aq_inner.aq_parent
    portal._delObject("reports")

    # remove reports from portal actions (top-right)
    portal_tabs = portal.portal_actions.portal_tabs
    portal_tabs.manage_delObjects("reports")

    # remove reports_workflow
    portal.portal_workflow.manage_delObjects(["senaite_reports_workflow"])

    # remove the portal type
    portal.portal_types.manage_delObjects(["Report", "ReportFolder"])

    logger.info("Removing legacy reports [DONE]")


@upgradestep(product, version)
def import_typeinfo(tool):
    """Import type info profile
    """

    # compatibility with DX migrations
    from senaite.core.upgrade.v02_06_000 import remove_at_portal_types
    remove_at_portal_types(tool)

    tool.runImportStepFromProfile(profile, "typeinfo")


def reindex_control_analyses(tool):
    """Reindex all reference/duplicate analyses
    """
    logger.info("Reindexing control analyses ...")

    query = {"portal_type": ["ReferenceAnalysis", "DuplicateAnalysis"]}
    brains = api.search(query, ANALYSIS_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        obj = api.get_object(brain)
        logger.info("Reindexing control analysis %d/%d: `%s`" % (
            num+1, total, api.get_path(obj)))
        obj.reindexObject()
        obj._p_deactivate()

    logger.info("Reindexing control analyses [DONE]")


def fix_samples_registered(tool):
    """Transitions the samples in "registered" status to a suitable status,
    either "sample_due", "recieved", or "to_be_sampled"
    """
    logger.info("Fixing samples in 'registered' status ...")

    setup = api.get_setup()
    auto_receive = setup.getAutoreceiveSamples()
    query = {"review_state": "sample_registered"}
    brains = api.search(query, SAMPLE_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Fixing samples in 'registered' status: {}/{}"
                        .format(num, total))

        sample = api.get_object(brain)

        # get the user who registered the sample
        creator = sample.Creator()

        if sample.getSamplingRequired():
            # sample has not been collected yet
            changeWorkflowState(sample, SAMPLE_WORKFLOW, "to_be_sampled",
                                actor=creator, action="to_be_sampled")
            sample.reindexObject()
            sample._p_deactivate()
            continue

        if auto_receive:
            user = security.get_user(creator)
            if user and user.has_permission(TransitionReceiveSample, sample):
                # Change status to sample_received
                changeWorkflowState(sample, SAMPLE_WORKFLOW, "sample_received",
                                    actor=creator, action="receive")

                # Mark the secondary as received
                alsoProvides(sample, IReceived)

                # Set same received date as created
                created = api.get_creation_date(sample)
                sample.setDateReceived(created)

                # Initialize analyses
                for obj in sample.objectValues():
                    if obj.portal_type != "Analysis":
                        continue
                    if api.get_review_status(obj) != "registered":
                        continue
                    changeWorkflowState(obj, ANALYSIS_WORKFLOW, "unassigned",
                                        actor=creator, action="initialize")
                    obj.reindexObject()
                    obj._p_deactivate()

                sample.reindexObject()
                sample._p_deactivate()
                continue

        # sample_due is the default initial status of the sample
        changeWorkflowState(sample, SAMPLE_WORKFLOW, "sample_due",
                            actor=creator, action="no_sampling_workflow")
        sample.reindexObject()
        sample._p_deactivate()

    logger.info("Fixing samples in 'registered' status [DONE]")


def fix_searches_worksheets(tool):
    """Reindex listing_searchable_text index from Worksheets
    """
    logger.info("Reindexing listing_searchable_text from Worksheets ...")
    request = api.get_request()
    cat = api.get_tool(WORKSHEET_CATALOG)
    cat.manage_reindexIndex("listing_searchable_text", REQUEST=request)
    logger.info("Reindexing listing_searchable_text from Worksheets [DONE]")


def fix_range_values(tool):
    """Fix possible min > max in reference definition/sample ranges
    """
    logger.info("Fix min/max for reference definitions and samples ...")
    fix_range_values_for(api.search({"portal_type": "ReferenceDefinition"}))
    # XXX: Reference Samples live in SENAITE CATALOG
    fix_range_values_for(api.search({"portal_type": "ReferenceSample"}))
    logger.info("Fix min/max for reference definitions and samples [DONE]")


def fix_range_values_for(brains):
    """Fix range values for the given brains
    """
    total = len(brains)
    for num, brain in enumerate(brains):
        obj = api.get_object(brain)
        reindex = False
        logger.info("Checking range values %d/%d: `%s`" % (
            num+1, total, api.get_path(obj)))
        rr = obj.getReferenceResults()
        for r in rr:
            r_key = r.get("keyword")
            r_min = api.to_float(r.get("min"), 0)
            r_max = api.to_float(r.get("max"), 0)

            # check if max > min
            if r_min > r_max:
                # set min value to the same as max value
                r["min"] = r["max"]
                logger.info(
                    "Fixing range values for service '{r_key}': "
                    "[{r_min},{r_max}] -> [{new_min},{new_max}]"
                    .format(
                        r_key=r_key,
                        r_min=r_min,
                        r_max=r_max,
                        new_min=r["min"],
                        new_max=r["max"],
                    ))
                reindex = True

            # check if error < 0
            r_err = api.to_float(r.get("error"), 0)
            if r_err < 0:
                r_err = abs(r_err)
                r["error"] = str(r_err)
                logger.info(
                    "Fixing negative error % for service '{r_key}: {r_err}"
                    .format(
                        r_key=r_key,
                        r_err=r["error"],
                    ))
                reindex = True

        if reindex:
            obj.reindexObject()
        obj._p_deactivate()


def purge_orphan_worksheets(tool):
    """Walks through all records from worksheets catalog and remove orphans
    """
    logger.info("Purging orphan Worksheet records from catalog ...")
    request = api.get_request()
    cat = api.get_tool(WORKSHEET_CATALOG)
    paths = cat._catalog.uids.keys()
    for path in paths:
        # try to wake-up the object
        obj = cat.resolve_path(path)
        if obj is None:
            obj = cat.resolve_url(path, request)

        if obj is None:
            # object is missing, remove
            logger.info("Removing stale record: {}".format(path))
            cat.uncatalog_object(path)
            continue

        obj._p_deactivate()

    logger.info("Purging orphan Worksheet records from catalog [DONE]")


def setup_client_landing_page(tool):
    """Setup the registry record for the client's landing page
    """
    logger.info("Setup client's default landing page ...")

    # compatibility with DX migrations
    from senaite.core.upgrade.v02_06_000 import remove_at_portal_types
    remove_at_portal_types(tool)

    # import the client registry
    import_registry(tool)

    # look for the legacy registry record
    key = "bika.lims.client.default_landing_page"
    value = api.get_registry_record(key, default="")

    # set the value to the new registry record
    vocab_key = "senaite.core.vocabularies.registry.client_landing_pages"
    vocab_factory = getUtility(IVocabularyFactory, vocab_key)
    vocabulary = vocab_factory(api.get_portal())
    values = [item.value for item in vocabulary]
    if value in values:
        set_registry_record(CLIENT_LANDING_PAGE, value)

    logger.info("Setup client's default landing page [DONE]")
