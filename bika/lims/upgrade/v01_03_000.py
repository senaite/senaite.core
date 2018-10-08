# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.3.0'  # Remember version number in metadata.xml and setup.py
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

    # -------- ADD YOUR STUFF BELOW --------

    # Remove QC reports and gpw dependency
    # https://github.com/senaite/senaite.core/pull/1058
    remove_qc_reports(portal)

    # Remove updates notification viewlet
    # https://github.com/senaite/senaite.core/pull/1059
    setup.runImportStepFromProfile(profile, 'viewlets')

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_qc_reports(portal):
    """Removes the action Quality Control from Reports
    """
    logger.info("Removing Reports > Quality Control ...")
    ti = portal.reports.getTypeInfo()
    actions = map(lambda action: action.id, ti._actions)
    for index, action in enumerate(actions, start=0):
        if action == 'qualitycontrol':
            ti.deleteActions([index])
            break
    logger.info("Removing Reports > Quality Control [DONE]")
