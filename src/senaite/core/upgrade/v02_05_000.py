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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.core import logger
from senaite.core.api.catalog import add_index
from senaite.core.api.catalog import del_index
from senaite.core.api.catalog import reindex_index
from senaite.core.catalog import CLIENT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.setuphandlers import add_dexterity_items
from senaite.core.setuphandlers import setup_catalog_mappings
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.upgrade.utils import uncatalog_brain

version = "2.5.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


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

    # -------- ADD YOUR STUFF BELOW --------

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def rebuild_sample_zctext_index_and_lexicon(tool):
    """Recreate sample listing_searchable_text ZCText index and Lexicon
    """
    # remove the existing index
    index = "listing_searchable_text"
    del_index(SAMPLE_CATALOG, index)
    # remove the Lexicon
    catalog = api.get_tool(SAMPLE_CATALOG)
    if "Lexicon" in catalog.objectIds():
        catalog.manage_delObjects("Lexicon")
    # recreate the index + lexicon
    add_index(SAMPLE_CATALOG, index, "ZCTextIndex")
    # reindex
    reindex_index(SAMPLE_CATALOG, index)


@upgradestep(product, version)
def setup_labels(tool):
    """Setup labels for SENAITE
    """
    logger.info("Setup Labels")
    portal = api.get_portal()

    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    tool.runImportStepFromProfile(profile, "plone.app.registry")
    setup_core_catalogs(portal)

    items = [
        ("labels",
         "Labels",
         "Labels")
    ]
    setup = api.get_senaite_setup()
    add_dexterity_items(setup, items)


def setup_client_catalog(tool):
    """Setup client catalog
    """
    logger.info("Setup Client Catalog ...")
    portal = api.get_portal()

    # setup and rebuild client_catalog
    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)
    client_catalog = api.get_tool(CLIENT_CATALOG)
    client_catalog.clearFindAndRebuild()

    # portal_catalog cleanup
    uncatalog_type("Client", catalog="portal_catalog")

    logger.info("Setup Client Catalog [DONE]")


def uncatalog_type(portal_type, catalog="portal_catalog", **kw):
    """Uncatalog all entries of the given type from the catalog
    """
    query = {"portal_type": portal_type}
    query.update(kw)
    brains = api.search(query, catalog=catalog)
    for brain in brains:
        uncatalog_brain(brain)


def setup_catalogs(tool):
    """Setup all core catalogs and ensure all indexes are present
    """
    logger.info("Setup Catalogs ...")
    portal = api.get_portal()

    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)

    logger.info("Setup Catalogs [DONE]")
