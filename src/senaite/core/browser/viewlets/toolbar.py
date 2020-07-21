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

from bika.lims.api.security import check_permission
from plone.app.layout.viewlets.common import PersonalBarViewlet
from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.browser.viewlets.languageselector import LanguageSelector
from senaite.core.browser.viewlets.sections import GlobalSectionsViewlet
from zope.component import getMultiAdapter
from zope.component import getUtility

LOGO = "/++plone++senaite.core.static/images/senaite.svg"


class ToolbarViewletManager(OrderedViewletManager):
    custom_template = ViewPageTemplateFile("templates/toolbar.pt")

    def base_render(self):
        return super(ToolbarViewletManager, self).render()

    def render(self):
        return self.custom_template()

    @property
    @memoize
    def context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )

    @property
    @memoize
    def portal(self):
        return self.portal_state.portal()

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state'
        )

    @memoize
    def is_manager(self):
        return check_permission("senaite.core: Manage Bika", self.portal)

    def get_personal_bar(self):
        viewlet = PersonalBarViewlet(
            self.context,
            self.request,
            self.__parent__, self
        )
        viewlet.update()
        return viewlet

    def get_toolbar_logo(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix="senaite", check=False)
        portal_url = self.portal_state.portal_url()
        try:
            logo = settings.toolbar_logo
        except AttributeError:
            logo = LOGO
        if not logo:
            logo = LOGO
        return portal_url + logo

    def get_lims_setup_url(self):
        portal_url = self.portal_state.portal().absolute_url()
        return "/".join([portal_url, "@@lims-setup"])

    def get_global_sections(self):
        viewlet = GlobalSectionsViewlet(
            self.context,
            self.request,
            self.__parent__, self
        )
        viewlet.update()
        return viewlet

    def get_language_selector(self):
        viewlet = LanguageSelector(
            self.context,
            self.request,
            self.__parent__, self
        )
        viewlet.update()
        return viewlet
