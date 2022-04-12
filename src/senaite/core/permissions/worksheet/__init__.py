# -*- coding: utf-8 -*-

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
