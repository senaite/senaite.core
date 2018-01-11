# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

from plone import api

version = '1.2.1'  # Remember version number in metadata.xml and setup.py
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
    pc = api.portal.get_tool('portal_catalog')
    pc.clearFindAndRebuild()

    bcal = api.portal.get_tool('bika_catalog_analysisrequest_listing')
    bcal.clearFindAndRebuild()

    bca = api.portal.get_tool('bika_analysis_catalog')
    bca.clearFindAndRebuild()

    logger.info("{0} upgraded to version {1}".format(product, version))

    return True
