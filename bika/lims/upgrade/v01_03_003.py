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
