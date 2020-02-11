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

from bika.lims import logger
from bika.lims import api
from bika.lims.catalog.analysisrequest_catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.2.7'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)
    setup = portal.portal_setup

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF HERE --------
    setup.runImportStepFromProfile(profile, 'workflow')
    update_permissions_rejected_analysis_requests()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def update_permissions_rejected_analysis_requests():
    """
    Maps and updates the permissions for rejected analysis requests so lab clerks, clients, owners and
    RegulatoryInspector can see rejected analysis requests on lists.

    :return: None
    """
    workflow_tool = api.get_tool("portal_workflow")
    workflow = workflow_tool.getWorkflowById('bika_ar_workflow')
    catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    brains = catalog(review_state='rejected')
    counter = 0
    total = len(brains)
    logger.info(
        "Changing permissions for rejected analysis requests. " +
        "Number of rejected analysis requests: {0}".format(total))
    for brain in brains:
        if 'LabClerk' not in brain.allowedRolesAndUsers:
            if counter % 100 == 0:
                logger.info(
                    "Changing permissions for rejected analysis requests: " +
                    "{0}/{1}".format(counter, total))
            obj = api.get_object(brain)
            workflow.updateRoleMappingsFor(obj)
            obj.reindexObject()
        counter += 1
    logger.info(
        "Changed permissions for rejected analysis requests: " +
        "{0}/{1}".format(counter, total))
