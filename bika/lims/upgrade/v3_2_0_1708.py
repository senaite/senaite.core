# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
import transaction
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from Products.CMFCore.utils import getToolByName

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
    ut.addIndexAndColumn(CATALOG_ANALYSIS_LISTING,
                         'getPrioritySortkey', 'FieldIndex')

    ut.refreshCatalogs()

    # Replace empty 'DateSampled' field with 'SamplingDate' of ARs,
    # which will take care of Samples as well.
    set_ar_date_sampled_fields(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def set_ar_date_sampled_fields(portal):
    """
    For old ARs has been created in Sampling Workflow Disabled mode,
    'Date Sampled' values are empty and 'Sampling Date' was "used" as 'Date Sampled'.
    Copy 'SamplingDate' values to 'DateSampled' if necessary.
    """
    uc = getToolByName(portal, CATALOG_ANALYSIS_REQUEST_LISTING)
    ars = uc(portal_type='AnalysisRequest')
    counter = 0
    tot_counter = 0
    total = len(ars)
    for ar in ars:
        # Only the ARS which has Sampling Date but not Date Sampled fields
        if not ar.getSamplingWorkflowEnabled and ar.getSamplingDate \
                        and not ar.getDateSampled:
            obj = ar.getObject()
            sd = obj.getSamplingDate()
            obj.setDateSampled(sd)
            obj.reindexObject()
            counter += 1

        tot_counter += 1
        if tot_counter % 500 == 0:
            logger.info(
                "Setting missing DateSampled values of "
                "ARs: %d of %d" % (tot_counter, total))
            transaction.commit()
    logger.info(
        "Done! 'DateSampled' field has been updated for %d "
        "AnalysisRequest objects." % counter)
