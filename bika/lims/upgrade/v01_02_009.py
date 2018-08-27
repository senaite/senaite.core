# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import time
import transaction

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

    # Reindex object security for client contents (see #991)
    reindex_client_local_owner_permissions(portal)

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
