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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api as ploneapi
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IFrontPageAdapter
from zope.component import getAdapters


class FrontPageView(BrowserView):
    """SENAITE default Front Page
    """
    template = ViewPageTemplateFile("templates/senaite-frontpage.pt")

    def __call__(self):
        self.icon = self.portal_url + "/++resource++bika.lims.images/chevron_big.png"
        bika_setup = getToolByName(self.context, "bika_setup")
        login_url = '{}/{}'.format(self.portal_url, 'login')
        landingpage = bika_setup.getLandingPage()

        # Anonymous Users get either redirected to the std. bika-frontpage or
        # to the custom landing page, which is set in bika_setup. If no landing
        # page setup, then redirect to login page.
        if self.is_anonymous_user():
            # Redirect to the selected Landing Page
            if landingpage:
                return self.request.response.redirect(landingpage.absolute_url())
            # Redirect to login page
            return self.request.response.redirect(login_url)

        # Authenticated Users get either the Dashboard, the std. login page
        # or the custom landing page. Furthermore, they can switch between the
        # Dashboard and the landing page.
        # Add-ons can have an adapter for front-page-url as well.
        for name, adapter in getAdapters((self.context,), IFrontPageAdapter):
            redirect_to = adapter.get_front_page_url()
            if redirect_to:
                return self.request.response.redirect(self.portal_url + redirect_to)

        # First precedence: Request parameter `redirect_to`
        redirect_to = self.request.form.get("redirect_to", None)
        if redirect_to == "dashboard":
            return self.request.response.redirect(self.portal_url + "/bika-dashboard")
        if redirect_to == "frontpage":
            if landingpage:
                return self.request.response.redirect(landingpage.absolute_url())
            return self.template()

        # Second precedence: Dashboard enabled
        if self.is_dashboard_enabled():
            roles = self.get_user_roles()
            allowed = ['Manager', 'LabManager', 'LabClerk']
            if set(roles).intersection(allowed):
                return self.request.response.redirect(
                    self.portal_url + "/bika-dashboard")
            if 'Sampler' in roles or 'SampleCoordinator' in roles:
                return self.request.response.redirect(self.portal_url + "/samples?samples_review_state=to_be_sampled")

        # Third precedence: Custom Landing Page
        if landingpage:
            return self.request.response.redirect(landingpage.absolute_url())

        # Last precedence: Front Page
        return self.template()

    def is_dashboard_enabled(self):
        """Checks if the dashboard is enabled
        """
        bika_setup = getToolByName(self.context, "bika_setup")
        return bika_setup.getDashboardByDefault()

    def is_anonymous_user(self):
        """Checks if the current user is anonymous
        """
        return ploneapi.user.is_anonymous()

    def get_user_roles(self):
        """Returns a list of roles for the current user
        """
        if self.is_anonymous_user():
            return []
        current_user = ploneapi.user.get_current()
        return ploneapi.user.get_roles(user=current_user)
