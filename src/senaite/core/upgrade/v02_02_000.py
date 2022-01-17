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
from senaite.core import logger
from senaite.core.config import PROJECTNAME as product
from senaite.core.setuphandlers import add_dexterity_setup_items
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.upgrade.utils import catalog_object
from senaite.core.upgrade.utils import copy_creators
from senaite.core.upgrade.utils import copy_dates
from senaite.core.upgrade.utils import copy_snapshots
from senaite.core.upgrade.utils import copy_workflow_history
from senaite.core.upgrade.utils import delete_object
from senaite.core.upgrade.utils import set_uid
from senaite.core.upgrade.utils import uncatalog_object

version = "2.2.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


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

    # run import steps located in senaite.core profiles
    setup.runImportStepFromProfile(profile, "typeinfo")
    setup.runImportStepFromProfile(profile, "workflow")

    # Add sample containers folder
    add_dexterity_setup_items(portal)

    # Migrate containes
    migrate_containers_to_dx(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def migrate_containers_to_dx(portal):
    """Converts existing containers to Dexterity
    """
    logger.info("Convert Containers to Dexterity ...")

    old_id = "bika_containers"
    new_id = "sample_containers"

    setup = api.get_setup()
    old = setup.get(old_id)
    new = setup.get(new_id)

    # return if the old container is already gone
    if not old:
        return

    # uncatalog the old object
    uncatalog_object(old)

    # copy items from old -> new container
    for src in old.objectValues():
        # extract the old values
        uid = api.get_uid(src)
        title = api.get_title(src)
        description = api.get_description(src)
        containertype = src.getRawContainerType()
        capacity = src.getCapacity()
        prepreserved = src.getPrePreserved()
        preservation = src.getRawPreservation()
        securityseal = src.getSecuritySealIntact()

        # uncatalog the old object
        uncatalog_object(src)

        # create the new DX object and set explicitly the values
        target = api.create(new, "SampleContainer", title=title)
        target.description = api.safe_unicode(description)
        target.containertype = [containertype] if containertype else []
        target.capacity = capacity if capacity else "0 ml"
        target.pre_preserved = prepreserved or False
        target.preservation = [preservation] if preservation else []
        target.security_seal_intact = securityseal or False

        # take over the UID
        set_uid(target, uid)
        # copy auditlog
        copy_snapshots(src, target)
        # copy creators
        copy_creators(src, target)
        # copy modification/creation dates
        copy_dates(src, target)
        # copy workflow history
        copy_workflow_history(src, target)
        # catalog the new object
        catalog_object(target)

    # copy snapshots for the container
    copy_snapshots(old, new)

    # delete the old object
    delete_object(old)

    logger.info("Convert Containers to Dexterity [DONE]")
