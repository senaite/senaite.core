# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.AdvancedQuery import Eq

from bika.lims import api
from bika.lims import logger
from bika.lims import permissions
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.2.8'  # Remember version number in metadata.xml and setup.py
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
    setup.runImportStepFromProfile(profile, 'workflow')

    client_contact_permissions_on_batches(portal, ut)

    # -------- ADD YOUR STUFF HERE --------

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def client_contact_permissions_on_batches(portal, ut):
    """
    Grants view permissions on batches folder in navtree
    :param portal: portal object
    :return: None
    """
    mp = portal.batches.manage_permission
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'RegulatoryInspector', 'Client'], 0)
    portal.batches.reindexObject()

    # Update batch object permissions
    workflow_tool = api.get_tool("portal_workflow")
    workflow = workflow_tool.getWorkflowById('bika_batch_workflow')
    catalog = api.get_tool('portal_catalog')

    # Update permissions programmatically
    query = Eq('portal_type', 'Batch') & ~ Eq('allowedRolesAndUsers', 'Client')
    brains = catalog.evalAdvancedQuery(query)
    counter = 0
    total = len(brains)
    logger.info(
        "Changing permissions for Batch objects: {0}".format(total))
    for brain in brains:
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject()
        counter += 1
        if counter % 100 == 0:
            logger.info(
                "Changing permissions for Batch objects: " +
                "{0}/{1}".format(counter, total))
    logger.info(
        "Changed permissions for Batch objects: " +
        "{0}/{1}".format(counter, total))
