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

from Products.Five.browser import BrowserView

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from senaite.core.api.worksheet import create_worksheet


class AddWorksheetView(BrowserView):
    """Handler for the "Add Worksheet" button in Worksheet Folder.
    If a template was selected, the worksheet is pre-populated here.
    """

    def __init__(self, context, request):
        super(AddWorksheetView, self).__init__(context, request)

    def __call__(self):
        if not self.request.form.get("submitted", False):
            return self.request.response.redirect(self.context.absolute_url())

        analyst = self.request.form.get("analyst", "")
        template = self.request.form.get("template", "")
        instrument = self.request.form.get("instrument", "")

        if not analyst:
            message = _(
                u"analyst_must_be_specified_message",
                default=u"Analyst must be specified.",
            )
            self.add_status_message(message, "warning")
            return self.request.response.redirect(self.context.absolute_url())

        ws = create_worksheet(analyst=analyst, instrument=instrument,
                              template=template)

        if not ws:
            message = _(
                u"worksheet_not_created",
                default=u"Worksheet not created.",
            )
            self.add_status_message(message, "error")
            return self.request.response.redirect(self.context.absolute_url())

        message = _(
            u"worksheet_created",
            default=u"Created worksheet ${ws_id}",
            mapping={"ws_id": ws.getId()},
        )
        self.add_status_message(message)
        return self.request.response.redirect(api.get_url(ws))

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
