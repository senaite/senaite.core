# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.1.0'
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

    # Required because of a mismatch between the view and workflow states
    # selector in Analysis Services view. See @93109be
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    # Remove indexes no longer used as per @daf57e3 and PR#307
    ut.delIndexAndColumn('bika_setup_catalog', 'getSortKey')
    ut.delIndexAndColumn('bika_setup_catalog', 'sortKey')

    # Add sortable_title index in analyses catalog, so analyses get sorted
    # automatically based on the same rules as Analysis Services do (PR#307):
    #   sortkey + title ascending
    ut.addIndex(CATALOG_ANALYSIS_LISTING, 'sortable_title', 'FieldIndex')
    ut.refreshCatalogs()

    # Do nothing, we just only want the profile version to be 1.0.0
    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
