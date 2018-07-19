# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import logger
from bika.lims import api
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.CMFCore import permissions

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

    # -------- ADD YOUR STUFF HERE --------

    # Revert upgrade actions performed due to #893 (reverted)
    revert_client_permissions_for_batches(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def revert_client_permissions_for_batches(portal):
    mp = portal.batches.manage_permission
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'RegulatoryInspector'], 0)
    portal.batches.reindexObject()

    wftool = api.get_tool("portal_workflow")
    batch_wf = wftool.getWorkflowById("bika_batch_workflow")
    acquire = False

    grant = ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'RegulatoryInspector', 'Verifier']
    batch_wf.states.open.setPermission("View", acquire, grant)

    grant = ['LabClerk', 'LabManager', 'Manager', 'RegulatoryInspector']
    batch_wf.states.closed.setPermission("View", acquire, grant)

    catalog = api.get_tool('portal_catalog')
    brains = catalog(portal_type='Batch')
    for brain in brains:
        allowed = brain.allowedRolesAndUsers or []
        if 'Client' not in allowed:
            # No need to do rolemapping + reindex if not necessary
            continue
        obj = api.get_object(brain)
        batch_wf.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=['allowedRolesAndUsers'])
        logger.info("Role mappings updated for {}".format(obj))
