# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import permissions

from bika.lims import logger
from bika.lims.permissions import CancelAndReinstate
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

product = 'bika.lims'
version = '3.2.0.1709'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ufrom = ut.getInstalledVersion(product)
    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ufrom, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True
    logger.info("Upgrading {0}: {1} -> {2}".format(product, ufrom, version))
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    set_methods_folder_permission(portal)
    set_laboratory_folder_permission(portal)
    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def set_methods_folder_permission(portal):
    """
    Modifying permissions for methods since anonymous users had access to them.
    :param portal: portal object
    :return: None
    """
    logger.info("Modifying permissions for methods.")
    mp = portal.methods.manage_permission
    mp(CancelAndReinstate, ['Manager', 'LabManager'], 0)
    mp(permissions.ListFolderContents, ['Member', 'Authenticated'], 0)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager'], 0)
    mp(permissions.DeleteObjects, ['Manager', 'LabManager'], 0)
    mp(permissions.View, ['Manager', 'Member', 'Authenticated'], 0)
    mp(permissions.AccessContentsInformation,
        ['Manager', 'Member', 'Authenticated'], 0)
    portal.methods.reindexObject()
    logger.info("Permissions for methods modified.")


def set_laboratory_folder_permission(portal):
    """
    Modifying permissions for laboratory since anonymous users had access
    to it.
    :param portal: portal object
    :return: None
    """
    logger.info("Modifying permissions for laboratory.")
    mp = portal.bika_setup.laboratory.manage_permission
    mp(permissions.AccessContentsInformation, ['Authenticated'], 0)
    mp(permissions.View, ['Authenticated'], 0)
    portal.bika_setup.laboratory.reindexObject()
    logger.info("Permissions for laboratory modified.")
