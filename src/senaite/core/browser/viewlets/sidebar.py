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

from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.portlets.interfaces import IPortletManager
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import navigation
from zope.component import getMultiAdapter
from zope.component import getUtility


class SidebarViewletManager(OrderedViewletManager):
    custom_template = ViewPageTemplateFile("templates/sidebar.pt")

    def base_render(self):
        return super(SidebarViewletManager, self).render()

    def render(self):
        return self.custom_template()

    def available(self):
        is_anonymous = self.portal_state.anonymous()
        return not is_anonymous

    @property
    @memoize
    def context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_context_state"
        )

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_portal_state"
        )

    def render_navigation_portlet(self):
        context = self.context_state.canonical_object()
        view = self.context.restrictedTraverse("@@plone")
        manager = getUtility(
            IPortletManager, name="plone.leftcolumn", context=context)
        assignment = navigation.Assignment(topLevel=0)
        renderer = getMultiAdapter(
            (self.context, self.request, view, manager, assignment),
            IPortletRenderer)
        return renderer.render()

    def is_navbar_toggled(self):
        return self.request.cookies.get("sidebar-toggle", None) == "true"
