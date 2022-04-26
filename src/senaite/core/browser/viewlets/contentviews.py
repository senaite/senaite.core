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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.layout.viewlets.common import ContentViewsViewlet as Base
from plone.memoize.view import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class ContentViewsViewlet(Base):
    index = ViewPageTemplateFile("templates/contentviews.pt")
    menu_template = ViewPageTemplateFile("templates/menu.pt")

    @property
    @memoize
    def context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_context_state")

    def is_action_selected(self, action):
        """Workaround for dysfunctional `selected` attribute in action
        """
        action_url = action.get('url')
        if not action_url:
            return action.get("selected", False)
        base_url = action_url.split("?")[0]
        return base_url == self.context_state.current_base_url()
