# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.analysisrequest_catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.2.5'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF HERE --------

    # Traceback when submitting duplicate when Duplicate Variation is not set
    # Walkthrough all analyses and analyses services and set 0.00 value for
    # DuplicateVariation if returns None
    # https://github.com/senaite/senaite.core/issues/768
    fix_duplicate_variation_nonfloatable_values()

    ut.addIndex(CATALOG_ANALYSIS_REQUEST_LISTING, "listing_searchable_text",
                "TextIndexNG3")
    ut.refreshCatalogs()
    logger.info("{0} upgraded to version {1}".format(product, version))

    return True

def fix_duplicate_variation_nonfloatable_values():
    # Update Analysis Services
    catalog = api.get_tool('bika_setup_catalog')
    brains = catalog(portal_type='AnalysisService')
    for brain in brains:
        service = api.get_object(brain)
        dup_var = service.getDuplicateVariation()
        if api.is_floatable(dup_var):
            continue
        service.setDuplicateVariation(0.0)
        logger.info("Updated Duplicate Variation for Service '%s': '0.0'" % (
                    service.Title()))

    # Update Analyses
    catalog = api.get_tool('bika_analysis_catalog')
    portal_types = ['Analysis', 'ReferenceAnalysis', 'DuplicateAnalysis']
    brains = catalog(portal_type=portal_types)
    for brain in brains:
        analysis = api.get_object(brain)
        dup_var = analysis.getDuplicateVariation()
        if api.is_floatable(dup_var):
            continue
        analysis.setDuplicateVariation(0.0)
        logger.info("Updated Duplicate Variation for Analysis '%s': '0.0'" % (
                    analysis.Title()))
