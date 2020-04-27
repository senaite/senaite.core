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
from bika.lims import permissions


def ObjectModifiedEventHandler(instance, event):
    """Actions to be taken when Setup object is modified
    """
    update_worksheet_manage_permissions(instance)


def update_worksheet_manage_permissions(senaite_setup):
    """Updates the permissions 'Manage Worksheets' and 'Edit Worksheet' based
    on the setting 'RestrictWorksheetManagement' from Setup
    """
    roles = ["LabManager", "Manager"]
    if not senaite_setup.getRestrictWorksheetManagement():
        # LabManagers, Analysts and LabClerks can create and manage worksheets
        roles.extend(["Analyst", "LabClerk"])

    worksheets = api.get_portal().worksheets
    worksheets.manage_permission(permissions.ManageWorksheets, roles, acquire=1)
    worksheets.manage_permission(permissions.EditWorksheet, roles, acquire=1)
    worksheets.reindexObject()
