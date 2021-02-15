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

from bika.lims import api
from bika.lims import logger
from bika.lims.catalog import BIKA_CATALOG
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import CATALOG_AUTOIMPORTLOGS_LISTING
from bika.lims.catalog import CATALOG_REPORT_LISTING
from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import del_metadata
from bika.lims.upgrade.utils import UpgradeUtils

version = "1.3.4"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

INDEXES_TO_ADD = [
    # List of tuples (catalog_name, index_name, index meta type)
    (CATALOG_ANALYSIS_REQUEST_LISTING, "modified", "DateIndex"),
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

    # Do not display clients folder to Clients. There is no need to do an
    # update-role-mappings of clients, cause the permissions at client level
    # have not changed, except that now they are acquire=1 for "active" status
    setup.runImportStepFromProfile(profile, "workflow")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("senaite_clients_workflow")
    workflow.updateRoleMappingsFor(portal.clients)
    portal.clients.reindexObject()

    # New link to My Organization
    setup.runImportStepFromProfile(profile, "actions")

    # Remove getObjectWorkflowStates metadata
    # https://github.com/senaite/senaite.core/pull/1579
    remove_object_workflow_states_metadata(portal)

    # Added "senaite.core: Transition: Retest" permission for analyses
    # Added transition "retest" in analysis workflow
    # https://github.com/senaite/senaite.core/pull/1580
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "workflow")
    update_workflow_mappings_for_to_be_verified(portal)

    # Unset/set specifications with dynamic results ranges assigned
    # https://github.com/senaite/senaite.core/pull/1588
    update_dynamic_analysisspecs(portal)

    # Users with Publisher role cannot publish samples
    update_workflow_mappings_contacts(portal)
    update_workflow_mappings_labcontacts(portal)
    update_workflow_mappings_samples(portal)

    # Add new indexes
    add_new_indexes(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_object_workflow_states_metadata(portal):
    """Removes the getObjectWorkflowStates metadata from catalogs
    """
    logger.info("Removing getObjectWorkflowStates metadata ...")
    catalogs = [
        BIKA_CATALOG,
        CATALOG_ANALYSIS_LISTING,
        CATALOG_ANALYSIS_REQUEST_LISTING,
        CATALOG_AUTOIMPORTLOGS_LISTING,
        CATALOG_REPORT_LISTING,
        CATALOG_WORKSHEET_LISTING,
        SETUP_CATALOG
    ]
    for catalog in catalogs:
        del_metadata(catalog, "getObjectWorkflowStates")

    logger.info("Removing getObjectWorkflowStates metadata [DONE]")


def update_workflow_mappings_for_to_be_verified(portal):
    """Updates the role mappings for analyses that are in "to_be_verfied"
    status, so the new transition "Retest" becomes available
    """
    logger.info("Updating role mappings for 'to_be_verified' analyses...")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("bika_analysis_workflow")
    query = {"portal_type": "Analysis",
             "review_state": "to_be_verified"}
    brains = api.search(query, CATALOG_ANALYSIS_LISTING)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}".format(num, total))
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
    logger.info("Updating role mappings for 'to_be_verified' analyses [DONE]")


def update_workflow_mappings_contacts(portal):
    """Updates the role mappings for clients contacts so users with Publisher
    role can publish samples
    """
    logger.info("Updating role mappings for Contacts ...")
    wf_id = "senaite_clientcontact_workflow"
    query = {"portal_type": "Contact"}
    brains = api.search(query, "portal_catalog")
    update_workflow_mappings_for(portal, wf_id, brains)
    logger.info("Updating role mappings for Contacts [DONE]")


def update_workflow_mappings_labcontacts(portal):
    """Updates the role mappings for lab contacts so users with Publisher
    role can publish samples
    """
    logger.info("Updating role mappings for Lab Contacts ...")
    wf_id = "senaite_labcontact_workflow"
    query = {"portal_type": "LabContact"}
    brains = api.search(query, "portal_catalog")
    update_workflow_mappings_for(portal, wf_id, brains)
    logger.info("Updating role mappings for Lab Contacts [DONE]")


def update_workflow_mappings_samples(portal):
    """Updates the role mappings for lab contacts so users with Publisher
    role can publish samples
    """
    logger.info("Updating role mappings for Samples ...")
    wf_id = "bika_ar_workflow"
    query = {"portal_type": "AnalysisRequest",
             "review_state": ["to_be_verified", "verified"]}
    brains = api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING)
    update_workflow_mappings_for(portal, wf_id, brains)
    logger.info("Updating role mappings for Samples [DONE]")


def update_workflow_mappings_for(portal, wf_id, brains):
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById(wf_id)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}".format(num, total))
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=["allowedRolesAndUsers"])


def update_dynamic_analysisspecs(portal):
    """Unset/set specifications that have dynamic result ranges assigned
    """

    # Skip update when there are no dynamic specs registered in the system
    setup = api.get_setup()
    dynamic_specs = getattr(setup, "dynamic_analysisspecs", None)
    if dynamic_specs is None:
        return
    if not dynamic_specs.objectIds():
        return

    logger.info("Updating specifications with dynamic results ranges...")
    catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    samples = catalog({"portal_type": "AnalysisRequest"})
    total = len(samples)

    logger.info("Checking dynamic specifications of {} samples".format(total))
    for num, sample in enumerate(samples):
        if num and num % 100 == 0:
            logger.info("Checked {}/{} samples".format(num, total))
        obj = api.get_object(sample)
        spec = obj.getSpecification()
        if spec is None:
            continue
        if not spec.getDynamicAnalysisSpec():
            continue

        # Unset/set the specification
        logger.info("Updating specification '{}' of smaple '{}'".format(
            spec.Title(), obj.getId()))

        obj.setSpecification(None)
        obj.setSpecification(spec)

    logger.info("Updating specifications with dynamic results ranges [DONE]")


def add_new_indexes(portal):
    logger.info("Adding new indexes ...")
    for catalog_id, index_name, index_metatype in INDEXES_TO_ADD:
        add_index(catalog_id, index_name, index_metatype)
    logger.info("Adding new indexes ... [DONE]")


def add_index(catalog_id, index_name, index_metatype):
    logger.info("Adding '{}' index to '{}' ...".format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name in catalog.indexes():
        logger.info("Index '{}' already in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.addIndex(index_name, index_metatype)
    logger.info("Indexing new index '{}' ...".format(index_name))
    catalog.manage_reindexIndex(index_name)
