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
from bika.lims.browser.workflow import WorkflowActionGenericAdapter
from bika.lims.workflow import doActionFor


class WorkflowActionRemoveAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of remove a worksheet
    """

    def __call__(self, action, objects):
        worksheet = self.context

        # Call the remove action
        doActionFor(worksheet, "remove")

        parent = api.get_parent(worksheet)
        url = api.get_url(parent)
        return self.redirect(redirect_url=url)
