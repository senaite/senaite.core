# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import VERSIONABLE_TYPES
from Products.CMFCore.utils import getToolByName
import traceback
import sys
import transaction

product = 'bika.lims'
version = '3.2.0.1705'


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

    # Remove versionable types
    logger.info("Removing versionable types...")
    portal_repository = getToolByName(portal, 'portal_repository')
    non_versionable = ['AnalysisSpec',
                       'ARPriority',
                       'Method',
                       'SamplePoint',
                       'SampleType',
                       'StorageLocation',
                       'WorksheetTemplate',]
    versionable = list(portal_repository.getVersionableContentTypes())
    vers = [ver for ver in versionable if ver not in non_versionable]
    portal_repository.setVersionableContentTypes(vers)
    logger.info("Versionable types updated: {0}".format(', '.join(vers)))

    # Add getId column to bika_catalog
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getNumberOfVerifications')
    # Add SearchableText index to analysis requests catalog
    ut.addIndex(
        CATALOG_ANALYSIS_REQUEST_LISTING, 'SearchableText', 'ZCTextIndex')
    # For reference samples
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getParentUID')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getDateSampled')

    # Reindexing bika_catalog_analysisrequest_listing in order to obtain the
    # correct getDateXXXs
    ut.addIndexAndColumn(
        CATALOG_ANALYSIS_REQUEST_LISTING, 'getDateVerified', 'DateIndex')
    if CATALOG_ANALYSIS_REQUEST_LISTING not in ut.refreshcatalog:
        ut.refreshcatalog.append(CATALOG_ANALYSIS_REQUEST_LISTING)

    # Deleting 'Html' field from ARReport objects.
    removeHtmlFromAR(portal)

    # Refresh affected catalogs
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def removeHtmlFromAR(portal):
    """
    'Html' StringField has been deleted from ARReport Schema.
    Now removing this attribute from old objects to save some memory.
    """
    uc = getToolByName(portal, 'uid_catalog')
    ar_reps = uc(portal_type='ARReport')
    f_name = 'Html'
    for ar in ar_reps:
        obj = ar.getObject()
        if hasattr(obj, f_name):
            delattr(obj, f_name)
            print 'R'
