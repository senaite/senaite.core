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
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.1.8'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)

INDEXES = [
    # catalog, id, indexed attribute, type
    ("bika_setup_catalog", "getSampleTypeTitle", "", "FieldIndex"),
    ("bika_setup_catalog", "getSampleTypeTitles", "", "KeywordIndex"),
]


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
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'plone.app.registry')
    upgrade_indexes()

    logger.info("{0} upgraded to version {1}".format(product, version))

    return True

def upgrade_indexes():
    logger.info("Fixing broken calculations (re-assignment of dependents)...")

    to_index = []
    for catalog, name, attribute, meta_type in INDEXES:
        c = api.get_tool(catalog)

        # get the index from the catalog
        index = c._catalog.indexes.get(name, None)

        # continue if the index exists and has the right meta type
        if index and index.meta_type == meta_type:
            logger.info("*** Index '{}' of type '{}' is already in catalog '{}'"
                        .format(name, meta_type, catalog))
            continue

        # remove the existing index with the wrong meta_type
        if index is not None:
            logger.info("*** Removing index '{}' from catalog '{}'"
                        .format(name, catalog))
            c._catalog.delIndex(name)

        # add the index with the right meta_type
        logger.info("*** Adding index '{}' of type '{}' to catalog '{}'"
                    .format(name, meta_type, catalog))
        c.addIndex(name, meta_type)
        to_index.append((catalog, name))

    for catalog, name in to_index:
        c = api.get_tool(catalog)
        logger.info("*** Indexing new index '{}' of catalog {} ..."
                    .format(name, catalog))
        c.manage_reindexIndex(name)
        logger.info("*** Indexing new index '{}' of catalog {} [DONE]"
                    .format(name, catalog))
