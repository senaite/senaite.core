# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.lims import logger
from bika.lims.catalog import getCatalogDefinitions, setup_catalogs
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

product = 'bika.lims'
version = '3.2.0.1704'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    ut = UpgradeUtils(portal)
    ufrom = ut.getInstalledVersion(product)
    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ufrom, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ufrom, version))

    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'toolset')

    # Updating lims catalogs if there is any change in them
    logger.info("Updating catalogs if needed...")
    catalog_definitions = getCatalogDefinitions()
    # Updating health catalogs if there is any change in them
    setup_catalogs(portal, catalog_definitions)
    logger.info("Catalogs updated")

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
