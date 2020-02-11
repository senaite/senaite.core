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

from plone.app.layout.viewlets.common import LogoViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class LogoViewlet(Base):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.logo.pt")

    def update(self):
        super(Base, self).update()

        portal = self.portal_state.portal()
        bprops = portal.restrictedTraverse("base_properties", None)
        if bprops is not None:
            logoName = bprops.logoName
        else:
            logoName = "logo.jpg"

        logoTitle = self.portal_state.portal_title()
        self.logo_tag = portal.restrictedTraverse(logoName).tag(
            title=logoTitle, alt=logoTitle, scale=0.5)
        self.navigation_root_title = self.portal_state.navigation_root_title()
