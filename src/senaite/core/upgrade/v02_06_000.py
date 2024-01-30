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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from plone.dexterity.fti import DexterityFTI
from senaite.core import logger
from senaite.core.config import PROJECTNAME as product
from senaite.core.interfaces import IContentMigrator
from senaite.core.setuphandlers import add_senaite_setup_items
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.upgrade.utils import copy_snapshots
from senaite.core.upgrade.utils import delete_object
from senaite.core.upgrade.utils import uncatalog_object
from zope.component import getMultiAdapter

version = "2.6.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

REMOVE_AT_TYPES = [
    "Department",
    "Departments",
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

    # -------- ADD YOUR STUFF BELOW --------

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_at_portal_types(portal):
    """Remove AT portal type information
    """
    logger.info("Remove AT types from portal_types tool ...")
    pt = api.get_tool("portal_types")
    for type_name in REMOVE_AT_TYPES:
        fti = pt.getTypeInfo(type_name)
        # keep DX FTIs
        if isinstance(fti, DexterityFTI):
            logger.info("Type '{}' is already a DX FTI".format(fti))
            continue
        elif not fti:
            # Removed already
            continue
        pt.manage_delObjects(fti.getId())
    logger.info("Remove AT types from portal_types tool ... [DONE]")


@upgradestep(product, version)
def migrate_departments_to_dx(tool):
    """Converts existing departments to Dexterity
    """
    logger.info("Convert Departments to Dexterity ...")

    # ensure old AT types are flushed first
    portal = api.get_portal()
    remove_at_portal_types(portal)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    old_id = "bika_departments"
    new_id = "departments"

    setup = api.get_senaite_setup()
    bikasetup = api.get_setup()

    old = bikasetup.get(old_id)
    new = setup.get(new_id)

    if not new:
        add_senaite_setup_items(portal)
        new = setup.get(new_id)

    # return if the old container is already gone
    if not all([old, new]):
        return

    # uncatalog the old object
    uncatalog_object(old)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
        "DepartmentID": ("getDepartmentID", "department_id", ""),
        "Manager": ("getManager", "manager", None),
    }

    # copy items from old -> new container
    for src in old.objectValues():
        target = new.get(src.getId())
        if not target:
            target = api.create(new, "Department")
        migrator = getMultiAdapter(
            (src, target), interface=IContentMigrator)
        migrator.migrate(schema_mapping, delete_src=False)

    # copy snapshots for the container
    copy_snapshots(old, new)

    # delete the old object
    delete_object(old)

    logger.info("Convert Departments to Dexterity [DONE]")
