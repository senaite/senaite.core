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

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.1.4'
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # Add inactive_state workflow for Reflex Rules
    setup.runImportStepFromProfile(profile, 'workflow')
    update_reflexrules_workflow_state(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def update_reflexrules_workflow_state(portal):
    """
    Updates Reflex Rules' inactive_state, otherwise they don't have it by
    default.
    :param portal: Portal object
    :return: None
    """
    wf_tool = getToolByName(portal, 'portal_workflow')
    logger.info("Updating Reflex Rules' 'inactive_state's...")
    wf = wf_tool.getWorkflowById("bika_inactive_workflow")
    uc = api.get_tool('portal_catalog')
    r_rules = uc(portal_type='ReflexRule')
    for rr in r_rules:
        obj = rr.getObject()
        wf.updateRoleMappingsFor(obj)
        obj.reindexObject()
    logger.info("Reflex Rules' 'inactive_state's were updated.")
