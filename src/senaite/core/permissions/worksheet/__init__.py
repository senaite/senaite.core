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

from bika.lims.api.security import check_permission
from .permissions import AddWorksheet
from .permissions import ManageWorksheets
from .permissions import EditWorksheet
from .permissions import WorksheetAddAttachment


def can_add_worksheet(context):
    """Checks if worksheets can be added in context
    """
    return check_permission(AddWorksheet, context)


def can_edit_worksheet(context):
    """Checks if worksheets can be managed in context
    """
    return check_permission(EditWorksheet, context)


def can_manage_worksheets(context):
    """Checks if worksheets can be managed in context
    """
    return check_permission(ManageWorksheets, context)


def can_add_worksheet_attachment(context):
    """Checks if attachments can be added to worksheet
    """
    return check_permission(WorksheetAddAttachment, context)
