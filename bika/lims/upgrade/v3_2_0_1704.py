# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
import traceback
import sys
import transaction

product = 'bika.lims'
version = '3.2.0.1704'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo(product)['installedVersion']
    logger.info("Upgrading {0}: {1} -> {2}".format(product, ufrom, version))

    ut = UpgradeUtils(portal)

    # Add getId column to bika_catalog
    ut.addColumn('bika_catalog', 'getId')

    # Refresh affected catalogs
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
