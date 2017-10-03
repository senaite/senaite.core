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

from bika.lims.catalog.sample_catalog import CATALOG_SAMPLE_LISTING
from bika.lims.catalog.sample_catalog import bika_catalog_sample_definition

from Products.CMFCore.utils import getToolByName

product = 'bika.lims'
version = '3.2.0.1709'


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

    # importing toolset in order to add bika_sample_catalog
    setup.runImportStepFromProfile('profile-bika.lims:default', 'toolset')

    create_sample_catalog(portal, ut)
    update_bika_catalog(portal, ut)
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def create_sample_catalog(portal, upgrade_utils):
    logger.info('Creating Sample catalog')
    at = getToolByName(portal, 'archetype_tool')
    catalog_dict = bika_catalog_sample_definition.get(CATALOG_SAMPLE_LISTING, {})
    sample_indexes = catalog_dict.get('indexes', {})
    sample_columns = catalog_dict.get('columns', [])
    # create sample catalog indexes
    for idx in sample_indexes:
        upgrade_utils.addIndex(CATALOG_SAMPLE_LISTING, idx, sample_indexes[idx])
    # create sample catalog columns
    for col in sample_columns:
        upgrade_utils.addColumn(CATALOG_SAMPLE_LISTING, col)

    # define objects to be catalogued
    at.setCatalogsByType('Sample', [CATALOG_SAMPLE_LISTING, ])
    logger.info('Recovering samples to reindex')
    # retrieve bika catalog and portal catalog so that samples can be uncatalogued
    bika_catalog = getToolByName(portal, 'bika_catalog')
    portal_catalog = getToolByName(portal, 'portal_catalog')
    # get brains of objects to be catalogued from bika catalog
    sample_brains = bika_catalog(portal_type='Sample')
    i = 0  # already indexed objects counter
    # reindex the found objects in the new sample catalog and uncatalog them from bika catalog
    logger.info('Reindexing samples')
    for brain in sample_brains:
        if i % 100 == 0:
            logger.info('Reindexed {}/{} samples'.format(i, len(sample_brains)))
            if i % 100 == 0:
                transaction.commit()
                logger.info('{0} items processed.'.format(i))
        sample_obj = brain.getObject()
        sample_obj.reindexObject()
        # uncatalog samples from bika catalog and portal catalog
        path_uid = '/'.join(sample_obj.getPhysicalPath())
        bika_catalog.uncatalog_object(path_uid)
        portal_catalog.uncatalog_object(path_uid)
        i += 1
    transaction.commit()
    logger.info('Reindexed {}/{} samples'.format(len(sample_brains), len(sample_brains)))

def update_bika_catalog(portal, upgrade_utils):
    # remove unnecessary columns and indexes from bika catalog
    # now that samples have their own catalog
    logger.info('Updating bika catalog')
    bika_catalog = getToolByName(portal, 'bika_catalog')
    unnecessary_cols = ['getSampleID', 'getRequestID', 'getClientOrderNumber', 'getClientReference',
                        'getClientSampleID', 'getSamplePointTitle', 'getSampleTypeTitle',
                        'getDatePublished', ]
    unnecessary_idxs = ['getDepartmentUIDs', 'getAnalysesUIDs', 'getClientOrderNumber', 'getClientReference',
                        'getClientSampleID', 'getClientTitle', 'getClientUID', 'getDatePublished',
                        'getInvoiced', 'getRequestID', 'getSampleID', 'getSamplePointTitle',
                        'getSamplePointUID', 'getSampler', 'getScheduledSamplingSampler',
                        'getSampleTypeTitle', 'getSampleTypeUID', 'getSampleUID', 'getSamplingDate',
                        'getWorksheetTemplateTitle', ]
    for column in unnecessary_cols:
        upgrade_utils.delColumn(bika_catalog, column)
    logger.info('Removed unnecessary columns')
    for index in unnecessary_idxs:
        upgrade_utils.delIndex(bika_catalog, index)
    logger.info('Removed unnecessary indexes')