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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Archetypes.config import UID_CATALOG

from bika.lims import api
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.setuphandlers import setup_form_controller_actions
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = "1.3.3"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

INDEXES_TO_ADD = [
    # Replaces getSampleTypeUIDs
    # https://github.com/senaite/senaite.core/pull/1481
    ("bika_setup_catalog", "sampletype_uids", "KeywordIndex"),

    # Replaces getAvailableMethodUIDs
    # Used to filter services in Worksheet's Add Analyses View for when the
    # Worksheet Template being used has a Method assigned.
    # https://github.com/senaite/senaite.core/pull/1481
    ("bika_setup_catalog", "method_available_uids", "KeywordIndex"),
]

INDEXES_TO_REMOVE = [
    # Only used in add2 to filter Sample Points by Sample Type when a Sample
    # Type was selected. Now, getSampleTypeUID is used instead because of
    # https://github.com/senaite/senaite.core/pull/1481
    ("bika_setup_catalog", "getSampleTypeTitles"),

    # Only used for when Sample and SamplePartition objects
    # existed. The following are the portal types stored in bika_catalog:
    #   Batch, BatchFolder and ReferenceSample
    # and there are no searches by getSampleTypeTitle for none of them
    ("bika_catalog", "getSampleTypeTitle"),

    # Not used neither for searches nor filtering of any of the content types
    # stored in bika_catalog (Batch, BatchFolder and ReferenceSample)
    ("bika_catalog", "getSampleTypeUID"),

    # getAccredited was only used in the "hidden" view accreditation to filter
    # services labeled as "accredited". Since we don't expect that listing to
    # contain too many items, they are now filtered by waking-up the object
    # https://github.com/senaite/senaite.core/pull/1484
    ("bika_setup_catalog", "getAccredited"),

    # getAnalyst index is used in Analyses (Duplicates and Reference included)
    # and Worksheets. None of the types stored in setup_catalog support Analyst
    # https://github.com/senaite/senaite.core/pull/1484
    ("bika_setup_catalog", "getAnalyst"),

    # getBlank index is not used in setup_catalog, but in bika_catalog, where
    # is used in AddControl and AddBlank views (Worksheet)
    # https://github.com/senaite/senaite.core/pull/1484
    ("bika_setup_catalog", "getBlank"),

    # Not used anywhere
    # https://github.com/senaite/senaite.core/pull/1484
    ("bika_setup_catalog", "getDuplicateVariation"),
    ("bika_setup_catalog", "getFormula"),


    # REPLACEMENTS (indexes to be removed because of a replacement)

    # getSampleTypeUID --> sampletype_uid (FieldIndex --> KeywordIndex)
    # https://github.com/senaite/senaite.core/pull/1481
    ("bika_setup_catalog", "getSampleTypeUID"),

    # getAvailableMethodUIDs --> method_available_uids
    # https://github.com/senaite/senaite.core/pull/1484
    ("bika_setup_catalog", "getAvailableMethodUIDs"),
]

METADATA_TO_REMOVE = [
    # Not used anywhere. In SamplePoints and Specifications listings, the
    # SampleType object is waken-up instead of calling the metadata
    ("bika_setup_catalog", "getSampleTypeTitle"),

    # getSampleTypeUID (as metadata field) is only used for analyses and
    # samples (AnalysisRequest), and none of the two are stored in setup_catalog
    ("bika_setup_catalog", "getSampleTypeUID"),

    # Only used for when Sample and SamplePartition objects existed.
    # The following are the portal types stored in bika_catalog:
    #   Batch, BatchFolder and ReferenceSample
    # and "getSampleTypeTitle" metadata is not used for none of them
    ("bika_catalog", "getSampleTypeTitle"),

    # Not used anywhere
    # https://github.com/senaite/senaite.core/pull/1484
    ("bika_setup_catalog", "getAccredited"),

    # Not used anywhere
    # https://github.com/senaite/senaite.core/pull/1484
    ("bika_setup_catalog", "getBlank"),
    ("bika_setup_catalog", "getDuplicateVariation"),
    ("bika_setup_catalog", "getFormula"),
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

    # https://github.com/senaite/senaite.core/pull/1469
    setup.runImportStepFromProfile(profile, "propertiestool")

    # Remove stale indexes and metadata
    # https://github.com/senaite/senaite.core/pull/1481
    remove_stale_indexes(portal)
    remove_stale_metadata(portal)

    # Add new indexes
    # https://github.com/senaite/senaite.core/pull/1481
    add_new_indexes(portal)

    # Reindex client's related fields (getClientUID, getClientTitle, etc.)
    # https://github.com/senaite/senaite.core/pull/1477
    reindex_client_fields(portal)

    # Redirect to worksheets folder when a Worksheet is removed
    # https://github.com/senaite/senaite.core/pull/1480
    setup_form_controller_actions(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def reindex_client_fields(portal):
    logger.info("Reindexing client fields ...")
    fields_to_reindex = [
        "getClientUID",
        "getClientID",
        "getClientTitle",
        "getClientURL"
    ]

    # We only need to reindex those that might be associated to a Client object.
    # There is no need to reindex objects that already belong to a Client.
    # Batches were correctly indexed in previous upgrade step
    portal_types = [
        "AnalysisProfile",
        "AnalysisSpec",
        "ARTemplate",
        "SamplePoint"
    ]

    query = dict(portal_type=portal_types)
    brains = api.search(query, UID_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Reindexing client fields: {}/{}".format(num, total))

        obj = api.get_object(brain)
        obj.reindexObject(idxs=fields_to_reindex)

    logger.info("Reindexing client fields ... [DONE]")


def remove_stale_indexes(portal):
    logger.info("Removing stale indexes ...")
    for catalog, index in INDEXES_TO_REMOVE:
        del_index(catalog, index)
    logger.info("Removing stale indexes ... [DONE]")


def remove_stale_metadata(portal):
    logger.info("Removing stale metadata ...")
    for catalog, column in METADATA_TO_REMOVE:
        del_metadata(catalog, column)
    logger.info("Removing stale metadata ... [DONE]")


def del_index(catalog_id, index_name):
    logger.info("Removing '{}' index from '{}' ..."
                .format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name not in catalog.indexes():
        logger.info("Index '{}' not in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.delIndex(index_name)


def del_metadata(catalog_id, column):
    logger.info("Removing '{}' metadata from '{}' ..."
                .format(column, catalog_id))
    catalog = api.get_tool(catalog_id)
    if column not in catalog.schema():
        logger.info("Metadata '{}' not in catalog '{}' [SKIP]"
                    .format(column, catalog_id))
        return
    catalog.delColumn(column)


def add_new_indexes(portal):
    logger.info("Adding new indexes ...")
    for catalog_id, index_name, index_metatype in INDEXES_TO_ADD:
        add_index(catalog_id, index_name, index_metatype)
    logger.info("Adding new indexes ... [DONE]")


def add_index(catalog_id, index_name, index_metatype):
    logger.info("Adding '{}' index to '{}' ...".format(index_name, catalog_id))
    catalog = api.get_tool(catalog_id)
    if index_name in catalog.indexes():
        logger.info("Index '{}' already in catalog '{}' [SKIP]"
                    .format(index_name, catalog_id))
        return
    catalog.addIndex(index_name, index_metatype)
    logger.info("Indexing new index '{}' ...".format(index_name))
    catalog.manage_reindexIndex(index_name)
