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

from bika.lims import logger, api
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.catalog.worksheet_catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.2.3'  # Remember version number in metadata.xml and setup.py
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

    # Unbound the worksheetanalysis_workflow from Analysis Requests and add a
    # FieldIndex 'assigned_state' in AR's catalog (for its use on searches)
    fix_assign_analysis_requests(portal, ut)

    # The number of QC Analyses is not refreshed when a Duplicate or Reference
    # Sample in a Worksheet. See #673. Thus, worksheets that are not yet in
    # to_be_verified state needs to be reindexed
    fix_worksheet_qc_number_analyses_inconsistences(portal, ut)

    logger.info("{0} upgraded to version {1}".format(product, version))

    return True


def fix_assign_analysis_requests(portal, ut):
    # Remove 'bika_worksheet_analysis_workflow' from AnalysisRequest
    wfid = 'bika_worksheetanalysis_workflow'
    wtool = api.get_tool('portal_workflow')
    chain = wtool.getChainFor('AnalysisRequest')
    if wfid in chain:
        # Remove the workflow from AR
        chain = [ch for ch in chain if ch != wfid]
        wtool.setChainForPortalTypes(['AnalysisRequest', ], chain)

    # Add the `assigned_state` index for Analysis Request catalog
    ut.addIndexAndColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'assigned_state',
                'FieldIndex')
    ut.refreshCatalogs()


def fix_worksheet_qc_number_analyses_inconsistences(portal, ut):
    query = {'portal_type': 'Worksheet',
             'review_state':'open'}
    brains = api.search(query, CATALOG_WORKSHEET_LISTING)
    for brain in brains:
        worksheet = api.get_object(brain)
        worksheet.reindexObject()
