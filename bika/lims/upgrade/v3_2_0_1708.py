# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from plone.api.portal import get_tool
from Products.CMFCore.utils import getToolByName
import transaction
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils import tmpID
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING

from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

from bika.lims.catalog.report_catalog import bika_catalog_report_definition
from bika.lims.catalog.report_catalog import CATALOG_REPORT_LISTING

product = 'bika.lims'
version = '3.2.0.1708'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ufrom = ut.getInstalledVersion(product)
    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ufrom, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ufrom, version))

    # Add missing Priority Index and Column to AR Catalog
    ut.addIndexAndColumn(CATALOG_ANALYSIS_REQUEST_LISTING,
                         'getPrioritySortkey', 'FieldIndex')
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True
