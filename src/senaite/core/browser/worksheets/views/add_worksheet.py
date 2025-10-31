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
from bika.lims import bikaMessageFactory as _
from senaite.core.config.worksheet import WORKSHEETS_FOLDER_ID


class AddWorksheetView(BrowserView):
    """Handler for the "Add Worksheet" button in Worksheet Folder.
    If a template was selected, the worksheet is pre-populated here.
    """

    def __init__(self, context, request):
        super(AddWorksheetView, self).__init__(context, request)

    def __call__(self):
        # Validation
        analyst = self.request.get("analyst", "")
        template = self.request.get("template", "")
        instrument = self.request.get("instrument", "")

        if not analyst:
            message = _(
                u"analyst_must_be_specified_message",
                default=u"Analyst must be specified.",
            )
            self.add_status_message(message, "warning")
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        portal = api.get_portal()
        ws_container = portal.get(WORKSHEETS_FOLDER_ID)
        ws = api.create(ws_container, "Worksheet")
        ws.setTitle(ws.getId())

        # Set analyst and instrument
        ws.setAnalyst(analyst)
        if instrument:
            ws.setInstrument(instrument)

        # Set the default layout for results display
        ws_layout = api.get_senaite_setup().getWorksheetLayout()
        ws.setResultsLayout(ws_layout)
        ws_url = ws.absolute_url()
        # overwrite saved context UID for event subscribers
        self.request["context_uid"] = ws.UID()

        # if no template was specified, redirect to blank worksheet
        if not template:
            self.request.RESPONSE.redirect(ws_url + "/add_analyses")
            return

        ws.applyWorksheetTemplate(template)
        ws.reindexObject()

        if ws.getLayoutView():
            self.request.RESPONSE.redirect(ws_url + "/manage_results")
        else:
            msg = _(
                u"no_analyses_were_added_message",
                default=u"No analyses were added",
            )
            self.add_status_message(msg)
            self.request.RESPONSE.redirect(ws_url + "/add_analyses")

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
