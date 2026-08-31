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
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IFrontPageAdapter
from plone import api as ploneapi
from senaite.core.config.registry import CLIENT_LANDING_PAGE
from senaite.core.registry import get_registry_record
from zope.component import getAdapters


class FrontPageView(BrowserView):
    """SENAITE Front Page

    Redirects to the dashboard. Anonymous users go to login.
    """

    def __call__(self):
        login_url = "{}/{}".format(self.portal_url, "login")
        dashboard_url = "{}/{}".format(
            self.portal_url, "senaite-dashboard")

        # Anonymous users go to login
        if ploneapi.user.is_anonymous():
            return self.request.response.redirect(login_url)

        # IFrontPageAdapter support (add-on hook)
        for name, adapter in getAdapters(
                (self.context,), IFrontPageAdapter):
            redirect_to = adapter.get_front_page_url()
            if redirect_to:
                return self.request.response.redirect(
                    self.portal_url + redirect_to)

        # Client users go to their client page
        client = api.get_current_client()
        if client:
            view = get_registry_record(CLIENT_LANDING_PAGE)
            url = "{}/{}".format(api.get_url(client), view)
            return self.request.response.redirect(url)

        # Everyone else goes to the dashboard
        return self.request.response.redirect(dashboard_url)
