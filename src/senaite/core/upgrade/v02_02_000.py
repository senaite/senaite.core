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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.core import logger
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils

version = "2.2.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------
    setup.runImportStepFromProfile(profile, "viewlets")
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "workflow")

    # Setup the permission for the edition of analysis conditions
    setup_edit_analysis_conditions(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def setup_edit_analysis_conditions(portal):
    """Updates role mappings for analyses that are not yet verified for the
    permission "Edit Analysis Conditions" to become effective
    """
    logger.info("Updating role mappings for Analyses ...")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("senaite_analysis_workflow")
    query = {
        "portal_type": "Analysis",
        "review_state": ["registered", "unassigned", "assigned"]
    }
    brains = api.search(query, ANALYSIS_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}".format(num, total))
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=["allowedRolesAndUsers"])

    logger.info("Updating role mappings for Analyses [DONE]")
