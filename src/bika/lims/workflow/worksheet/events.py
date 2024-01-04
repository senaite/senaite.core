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

from bika.lims import api
from bika.lims import workflow as wf


def after_retract(worksheet):
    """Retracts all analyses the worksheet contains
    """
    for analysis in worksheet.getAnalyses():
       wf.doActionFor(analysis, "retract")


def after_remove(worksheet):
    """Removes the worksheet from the system
    """
    # bypass security checks on object removal. The removal of worksheet
    # objects is governed by "Transition: Remove Worksheet" permission at
    # worksheet level, along with a specific guard to ensure that only empty
    # worksheets can be removed. Therefore, better keep the "Delete objects"
    # permission at Worksheets folder level as false, because is less specific
    api.delete(worksheet, check_permissions=False)
