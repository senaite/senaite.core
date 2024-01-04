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
from bika.lims.browser import ulocalized_time
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SampleDispatchedViewlet(ViewletBase):
    """Print a viewlet showing the WF history comment
    """
    template = ViewPageTemplateFile("templates/sample_dispatched_viewlet.pt")

    def __init__(self, context, request, view, manager=None):
        super(SampleDispatchedViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view

    def is_dispatched(self):
        """Returns whether the current sample is dispatched
        """
        return api.get_review_status(self.context) == "dispatched"

    def get_state_info(self):
        """Returns the WF state information
        """
        history = api.get_review_history(self.context)
        entry = len(history) and history[0] or {}
        actor = entry.get("actor")
        user = api.user.get_user(actor)
        if user:
            actor = user.getProperty("fullname", actor)
        date = entry.get("time")
        comments = entry.get("comments", "")

        return {
            "actor": actor,
            "date": self.ulocalized_time(date, long_format=1),
            "comments": api.safe_unicode(comments),
        }

    def index(self):
        if self.is_dispatched():
            return ""
        return self.template()

    def ulocalized_time(self, time, long_format=None, time_only=None):
        return ulocalized_time(time, long_format, time_only,
                               context=self.context, request=self.request)
