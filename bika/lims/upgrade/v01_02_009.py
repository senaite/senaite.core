# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.2.9'  # Remember version number in metadata.xml and setup.py
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
    migrate_attachment_report_options(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def migrate_attachment_report_options(portal):
    """Migrate Attachments with the report option "a" (attach in report)
       to the option to "i" (ignore in report)
    """
    attachments = api.search({"portal_type": "Attachment"})
    total = len(attachments)
    logger.info("Migrating 'Attach to Report' -> 'Ingore in Report' "
                "for %d attachments" % total)
    for num, attachment in enumerate(attachments):
        obj = api.get_object(attachment)

        if obj.getReportOption() in ["a", ""]:
            obj.setReportOption("i")
            obj.reindexObject()
            logger.info("Migrated Attachment %s" % obj.getTextTitle())
