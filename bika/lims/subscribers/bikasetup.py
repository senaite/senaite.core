# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName

from bika.lims.permissions import ManageWorksheets


def BikaSetupModifiedEventHandler(instance, event):
    """ Event fired when BikaSetup object gets modified.
        Applies security and permission rules
    """

    if instance.portal_type != "BikaSetup":
        print("How does this happen: type is %s should be BikaSetup" % instance.portal_type)
        return

    # Security
    portal = getToolByName(instance, 'portal_url').getPortalObject()
    mp = portal.manage_permission
    if instance.getRestrictWorksheetManagement() == True \
        or instance.getRestrictWorksheetUsersAccess() == True:
        # Only LabManagers are able to create worksheets.
        mp(ManageWorksheets, ['Manager', 'LabManager'],1)
    else:
        # LabManagers, Lab Clerks and Analysts can create worksheets
        mp(ManageWorksheets, ['Manager', 'LabManager', 'LabClerk', 'Analyst'],1)
