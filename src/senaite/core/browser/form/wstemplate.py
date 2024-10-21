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

from bika.lims.browser import BrowserView
from senaite.core.interfaces import IWorksheetTemplate
from senaite.core.interfaces import IWorksheetTemplates


class UpdateNumPositions(BrowserView):
    """Changing number of positions for template layout from add/edit form
    """

    def __call__(self):
        url = self.context.absolute_url()
        sub_path = ""
        num = self.request.form.get("form.widgets.num_of_positions", 0)
        if IWorksheetTemplate.providedBy(self.context):
            self.context.setNumOfPositions(num)
            sub_path = "edit"
        elif IWorksheetTemplates.providedBy(self.context):
            sub_path = "++add++WorksheetTemplate?num_positions={}".format(num)

        url = "/".join([url, sub_path])
        return self.request.response.redirect(url)
