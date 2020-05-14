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
