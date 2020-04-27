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
from bika.lims.catalog.analysisrequest_catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore import permissions

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

    # Lab Managers can not remove Analyses in "Manage Analyses" form
    fix_permission_on_analysisrequests()

    # Traceback when submitting duplicate when Duplicate Variation is not set
    # Walkthrough all analyses and analyses services and set 0.00 value for
    # DuplicateVariation if returns None
    # https://github.com/senaite/senaite.core/issues/768
    fix_duplicate_variation_nonfloatable_values()

    # Analyses submission in Worksheets is slow
    # Remove "_LatestReferenceAnalyses" ReferenceField. Is not used anymore,
    # https://github.com/senaite/senaite.core/pull/776
    del_at_refs('InstrumentLatestReferenceAnalyses')

    # Make searches in Analysis Request listings faster
    # https://github.com/senaite/senaite.core/pull/771
    ut.addIndex(CATALOG_ANALYSIS_REQUEST_LISTING, "listing_searchable_text",
                "TextIndexNG3")

    ut.refreshCatalogs()
    logger.info("{0} upgraded to version {1}".format(product, version))

    return True


def fix_permission_on_analysisrequests():
    catalog = api.get_tool(CATALOG_ANALYSIS_REQUEST_LISTING)
    valid_states = ['sample_due', 'sample_received', 'sampled',
                    'to_be_sampled', 'to_be_preserved']
    brains = catalog(cancellation_state='active', review_state=valid_states)
    for brain in brains:
        obj = api.get_object(brain)
        mp = obj.manage_permission
        mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
        logger.info("Fixed '{}' permission on '{}'".format(
            permissions.DeleteObjects, obj.Title()))


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

def del_at_refs(relationship, pgthreshold=100):
    rc = api.get_tool(REFERENCE_CATALOG)
    refs = rc(relationship=relationship)
    if not refs:
        return

    logger.info("Found {} refs for {}".format(len(refs), relationship))
    total = len(refs)
    removed = 0
    for ref in refs:
        ref_object = ref.getObject()
        if ref_object:
            ref_object.aq_parent.manage_delObjects([ref.UID])
        removed+=1
        if removed % pgthreshold == 0:
            ratio = '%.2f' % (float(removed) * 100 / float(total))
            msg = "Removed {0}/{1} references ({2}%)"
            logger.info(msg.format(removed, total, ratio))
    if removed:
        logger.info("Performed {} deletions".format(removed))
