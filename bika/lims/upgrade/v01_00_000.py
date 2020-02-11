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

from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.config import  PROJECTNAME as product

version = '1.0.0'
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    # Since this upgrade is precisely meant to establish a version regardless
    # of the version numbering at bikalims/bika.lims, we don't want this check
    # to be performed.
    #if ut.isOlderVersion(product, version):
    #    logger.info("Skipping upgrade of {0}: {1} > {2}".format(
    #        product, ufrom, version))
    #    # The currently installed version is more recent than the target
    #    # version of this upgradestep
    #    return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # Do nothing, we just only want the profile version to be 1.0.0
    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
