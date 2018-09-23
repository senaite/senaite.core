# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import time
import transaction
from Products.Archetypes.config import REFERENCE_CATALOG

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

    # Reindex object security for client contents (see #991)
    reindex_client_local_owner_permissions(portal)

    # Rebind ARs that were generated because of the retraction of other ARs
    rebind_retracted_ars(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def reindex_client_local_owner_permissions(portal):
    """https://github.com/senaite/senaite.core/issues/957 Reindex bika_setup
    objects located in clients to give proper permissions to client contacts.
    """
    start = time.time()
    bsc = portal.bika_setup_catalog
    uids = [c.UID() for c in portal.clients.objectValues()]
    brains = bsc(getClientUID=uids)
    total = len(brains)
    for num, brain in enumerate(brains):
        ob = brain.getObject()
        logger.info("Reindexing permission for {}/{} ({})"
                    .format(num, total, ob.absolute_url()))
        ob.reindexObjectSecurity()
    end = time.time()
    logger.info("Fixing local owner role on client objects took {:.2f}s"
                .format(end-start))
    transaction.commit()

    
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


def rebind_retracted_ars(portal):
    """Rebind the ARs automatically generated because of the retraction of their
    parent to the new field 'Retracted'. The field used until now
    'ParentAnalysisRequest' will be used for partitioning
    """
    logger.info("Rebinding retracted/invalidated ARs")

    # Walk through the Analysis Requests that were generated because of a
    # retraction, get the source AR and rebind the fields
    relationship = "AnalysisRequestChildAnalysisRequest"
    ref_catalog = api.get_tool(REFERENCE_CATALOG)
    retests = ref_catalog(relationship=relationship)
    total = len(retests)
    num = 0
    for num, relation in enumerate(retests, start=1):
        relation = relation.getObject()
        if not relation:
            continue
        retest = relation.getTargetObject()
        retracted = relation.getSourceObject()
        retest.setRetracted(retracted)
        # Set ParentAnalysisRequest field to None, cause we will use this field
        # for storing Primary-Partitions relationship.
        retest.setParentAnalysisRequest(None)

        # Remove the relationship!
        relation.aq_parent.manage_delObjects([relation.id])

        if num % 100 == 0:
            logger.info("Rebinding retracted ARs: {0}/{1}".format(num, total))

    logger.info("{} retracted ARs have been rebinded".format(num))