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
from bika.lims import permissions

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
    client_contact_permissions_on_batches_folder(portal)

    # -------- ADD YOUR STUFF HERE --------

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def client_contact_permissions_on_batches_folder(portal):
    """
    Grants view permissions on batches folder in navtree
    :param portal: portal object
    :return: None
    """
    mp = portal.batches.manage_permission
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'RegulatoryInspector', 'Client'], 0)
    portal.batches.reindexObject()
