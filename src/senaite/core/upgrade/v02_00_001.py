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
from Products.ZCatalog.ProgressHandler import ZLogHandler
from senaite.core import logger
from senaite.core.api.catalog import add_column
from senaite.core.api.catalog import add_index
from senaite.core.api.catalog import get_columns
from senaite.core.api.catalog import get_index
from senaite.core.api.catalog import get_indexes
from senaite.core.config import PROJECTNAME as product
from senaite.core.setuphandlers import setup_auditlog_catalog_mappings
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils

version = "2.0.1"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

MIGRATE_CATALOGS = [
    ("auditlog_catalog", "senaite_catalog_auditlog"),
    ("bika_analysis_catalog", "senaite_catalog_analysis"),
    ("bika_catalog", "senaite_catalog"),
    ("bika_catalog_analysisrequest_listing", "senaite_catalog_sample"),
    ("bika_catalog_autoimportlogs_listing", "senaite_catalog_autoimportlog"),
    ("bika_catalog_report", "senaite_catalog_report"),
    ("bika_catalog_worksheet_listing", "senaite_catalog_worksheet"),
    ("bika_setup_catalog", "senaite_catalog_setup"),
]


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup  # noqa
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------
    setup.runImportStepFromProfile(profile, "actions")
    setup.runImportStepFromProfile(profile, "workflow")

    fix_types_i18n_domain(portal)

    # https://github.com/senaite/senaite.core/pull/1872
    migrate_catalogs(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def fix_types_i18n_domain(portal):
    """Walks through portal types and assigns the 'senaite.core` domain to
    those types from senaite
    """
    products = ["bika.lims", "senaite.core"]
    pt = api.get_tool("portal_types")
    for fti in pt.listTypeInfo():
        if fti.product in products:
            if fti.i18n_domain != "senaite.core":
                fti.i18n_domain = "senaite.core"


def migrate_catalogs(portal):
    """Migrate catalogs to Senaite
    """
    logger.info("Migrate catalogs to Senaite...")
    # 1. Install new core catalogs
    setup_core_catalogs(portal)
    # 2. Setup auditog catalog
    setup_auditlog_catalog_mappings(portal)

    # 3. Migrate old -> new indexes
    for src_cat_id, dst_cat_id in MIGRATE_CATALOGS:
        logger.info("Migrating catalog %s -> %s" %
                    (src_cat_id, dst_cat_id))

        src_cat = getattr(portal, src_cat_id, None)
        dst_cat = getattr(portal, dst_cat_id, None)

        if src_cat is None:
            logger.info("Source catalog '%s' not found [SKIP]")
            continue

        # ensure indexes
        for index in get_indexes(src_cat):
            if index not in get_indexes(dst_cat):
                index_obj = get_index(src_cat, index)
                index_type = index_obj.__class__.__name__
                # convert TextIndexNG3 to ZCTextIndex
                if index_type == "TextIndexNG3":
                    index_type = "ZCTextIndex"
                add_index(dst_cat, index, index_type)
                logger.info("Added missing index %s('%s') to %s"
                            % (index_type, index, dst_cat_id))

        # ensure columns
        for column in get_columns(src_cat):
            if column not in get_columns(dst_cat):
                add_column(dst_cat, column)
                logger.info("Added missing column %s to %s"
                            % (column, dst_cat_id))

        # copy over internal catalog structure from internal Catalog:
        #
        # self.data = IOBTree()  # mapping of rid to meta_data
        # self.uids = OIBTree()  # mapping of uid to rid
        # self.paths = IOBTree()  # mapping of rid to uid
        dst_cat._catalog.data = src_cat._catalog.data
        dst_cat._catalog.uids = src_cat._catalog.uids
        dst_cat._catalog.paths = src_cat._catalog.paths

        # refesh the catalog
        pghandler = ZLogHandler(100)
        dst_cat.refreshCatalog(pghandler=pghandler)

        # delete old catalog
        portal.manage_delObjects([src_cat_id])

    # Update archetype tool
    at = api.get_tool("archetype_tool")
    for portal_type, catalogs in at.catalog_map.items():
        at.setCatalogsByType(portal_type, catalogs)

    logger.info("Migrate catalogs to Senaite [DONE]")
