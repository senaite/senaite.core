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


class WorksheetView(BrowserView):
    """Base view for Worksheet
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        view = "manage_results"
        if not self.context.getRawAnalyses():
            view = "add_analyses"
            msg = _(
                u"no_analyses_were_added_message",
                default=u"No analyses were added",
            )
            self.context.plone_utils.addPortalMessage(msg, "info")

        ws_url = api.get_url(self.context)
        redirect_url = "{}/{}".format(ws_url, view)
        return self.request.response.redirect(redirect_url)
