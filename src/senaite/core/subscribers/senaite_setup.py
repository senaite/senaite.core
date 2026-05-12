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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.core.permissions import AddWorksheet
from senaite.core.permissions import EditWorksheet
from senaite.core.permissions import ManageWorksheets


def on_senaite_setup_modified(senaite_setup, event):
    """Updates the permissions 'Manage Worksheets' and 'Edit Worksheet' based
    on the setting 'restrict_worksheet_management' from Senaite Setup
    """
    update_worksheets_permissions(senaite_setup)


def update_worksheets_permissions(senaite_setup):
    """Updates the permissions 'Manage Worksheets' and 'Edit Worksheet' based
    on the setting 'restrict_worksheet_management' from Senaite Setup
    """
    roles = ["LabManager", "Manager"]
    restrict = senaite_setup.getRestrictWorksheetManagement()
    if not restrict:
        # LabManagers, Analysts and LabClerks can create and manage worksheets
        roles.extend(["Analyst", "LabClerk"])

    worksheets = api.get_portal().worksheets
    worksheets.manage_permission(AddWorksheet, roles, acquire=1)
    worksheets.manage_permission(ManageWorksheets, roles, acquire=1)
    worksheets.manage_permission(EditWorksheet, roles, acquire=1)
    worksheets.reindexObject()
