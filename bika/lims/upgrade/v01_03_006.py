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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.Archetypes.config import REFERENCE_CATALOG

version = "1.3.6"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


METADATA_TO_REMOVE = [
    # No longer used, see https://github.com/senaite/senaite.core/pull/2051/
    (CATALOG_ANALYSIS_LISTING, "getAnalyst"),
    (CATALOG_ANALYSIS_LISTING, "getAnalystName"),
]


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------
    setup.runImportStepFromProfile(profile, "rolemap")

    remove_stale_metadata(portal)

    fix_worksheets_analyses(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_stale_metadata(portal):
    """Remove metadata columns no longer used
    """
    logger.info("Removing stale metadata ...")
    for catalog, column in METADATA_TO_REMOVE:
        del_metadata(catalog, column)
    logger.info("Removing stale metadata ... [DONE]")


def del_metadata(catalog_id, column):
    logger.info("Removing '{}' metadata from '{}' ..."
                .format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column not in catalog.schema():
        logger.info("Metadata '{}' not in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.delColumn(column)


def fix_worksheets_analyses(portal):
    logger.info("Fix Worksheets Analyses ...")
    worksheets = portal.worksheets.objectValues()
    total = len(worksheets)
    for num, worksheet in enumerate(worksheets):
        if num and num % 10 == 0:
            logger.info("Processed worksheets: {}/{}".format(num, total))
        fix_worksheet_analyses(worksheet)
    logger.info("Fix Worksheets Analyses [DONE]")


def fix_worksheet_analyses(worksheet):
    """Purge worksheet analyses based on the layout and removes the obsolete
    relationship from reference_catalog
    """
    # Get the referenced analyses via relationship
    analyses = worksheet.getRefs(relationship="WorksheetAnalysis")
    analyses_uids = [api.get_uid(an) for an in analyses]

    new_layout = []
    for slot in worksheet.getLayout():
        uid = slot.get("analysis_uid")
        if not api.is_uid(uid):
            continue

        if uid not in analyses_uids:
            if is_orphan(uid):
                continue

        new_layout.append(slot)

    # Re-assign the analyses
    uids = [slot.get("analysis_uid") for slot in new_layout]
    worksheet.setAnalyses(uids)
    worksheet.setLayout(new_layout)

    # Remove all records for this worksheet from reference catalog
    tool = api.get_tool(REFERENCE_CATALOG)
    tool.deleteReferences(worksheet, relationship="WorksheetAnalysis")


def is_orphan(uid):
    """Returns whether a counterpart object exists for the given UID
    """
    obj = api.get_object_by_uid(uid, None)
    return obj is None
