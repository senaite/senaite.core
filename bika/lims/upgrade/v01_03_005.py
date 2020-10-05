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
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = "1.3.5"  # Remember version number in metadata.xml and setup.py
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

    # Fix writing methods on read when reindexing services
    # https://github.com/senaite/senaite.core/pull/1617
    remove_duplicate_methods_in_services(portal)

    # Published results tab is not displayed to client contacts
    # https://github.com/senaite/senaite.core/pull/1629
    fix_published_results_permission(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_duplicate_methods_in_services(portal):
    """A bug caused duplicate methods stored in services which need to be fixed
    """
    logger.info("Remove duplicate methods from services...")

    cat = api.get_tool(SETUP_CATALOG)
    services = cat({"portal_type": "AnalysisService"})
    total = len(services)

    for num, service in enumerate(services):
        if num and num % 10 == 0:
            logger.info("Processed {}/{} Services".format(num, total))
        obj = api.get_object(service)
        methods = list(set(obj.getRawMethods()))
        if not methods:
            continue
        obj.setMethods(methods)
        obj.reindexObject()

    logger.info("Remove duplicate methods from services [DONE]")


def fix_published_results_permission(portal):
    """Resets the permissions for action 'published_results' from
    AnalysisRequest portal type to 'View'
    """
    ti = portal.portal_types.getTypeInfo("AnalysisRequest")
    for action in ti.listActions():
        if action.id == "published_results":
            action.permissions = ("View", )
            break
