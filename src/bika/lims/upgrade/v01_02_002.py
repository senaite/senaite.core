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

from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import logger
from bika.lims.catalog.worksheet_catalog import CATALOG_WORKSHEET_LISTING
from bika.lims.browser.dashboard.dashboard import \
    setup_dashboard_panels_visibility_registry
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.vocabularies import getStickerTemplates

version = '1.2.2'  # Remember version number in metadata.xml and setup.py
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

    # Issue #574: Client batch listings are dumb.  This requires Batches to
    # be reindexed, as thy now provide an accessor for getClientUID.
    reindex_batch_getClientUID(portal)

    # The catalog where worksheets are stored (bika_catalog_worksheet_listing)
    # had a FieldIndex "WorksheetTemplate" which was causing a TypeError (can't
    # pickle acquisition wrappers) when reindexing worksheets with an associated
    # Worksheet Template.
    fix_worksheet_template_index(portal, ut)

    # Adds an entry to the registry to store the roles that can see Samples
    # section from Dashboard
    add_sample_section_in_dashboard(portal)

    # Ability to choose the sticker templates based on sample types (#607)
    set_sample_type_default_stickers(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))

    return True


def reindex_batch_getClientUID(portal):
    rc = getToolByName(portal, REFERENCE_CATALOG)
    brains = rc(portal_type='Batch')
    for brain in brains:
        batch = brain.getObject()
        batch.reindexObject(idxs=['getClientUID'])


def fix_worksheet_template_index(portal, ut):
    ut.delIndex(CATALOG_WORKSHEET_LISTING, 'getWorksheetTemplate')
    ut.addIndex(CATALOG_WORKSHEET_LISTING, 'getWorksheetTemplateTitle',
                'FieldIndex')
    ut.refreshCatalogs()

    
def add_sample_section_in_dashboard(portal):
    setup_dashboard_panels_visibility_registry('samples')

def set_sample_type_default_stickers(portal):
    """
    Fills the admitted stickers and their default stickers to every sample
    type.
    """
    # Getting all sticker templates
    stickers = getStickerTemplates()
    sticker_ids = []
    for sticker in stickers:
        sticker_ids.append(sticker.get('id'))
    def_small_template = portal.bika_setup.getSmallStickerTemplate()
    def_large_template = portal.bika_setup.getLargeStickerTemplate()
    # Getting all Sample Type objects
    catalog = api.get_tool('bika_setup_catalog')
    brains = catalog(portal_type='SampleType')
    for brain in brains:
        obj = api.get_object(brain)
        if obj.getAdmittedStickers() is not None:
            continue
        obj.setAdmittedStickers(sticker_ids)
        obj.setDefaultLargeSticker(def_large_template)
        obj.setDefaultSmallSticker(def_small_template)
