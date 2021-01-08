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

from plone.app.layout.viewlets.common import ViewletBase
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.utils import getSiteLogo
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility

LOGO_URL = "++plone++senaite.core.static/images/senaite-site-logo.png"


class LogoViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/logo.pt")

    def update(self):
        super(LogoViewlet, self).update()

        # TODO: should this be changed to settings.site_title?
        self.navigation_root_title = self.portal_state.navigation_root_title()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False)

        self.logo_title = settings.site_title
        self.logo_width = getattr(settings, "site_logo_width", "200px")
        self.logo_height = getattr(settings, "site_logo_height", "")

        # XXX: Seems that this override fails with Python 2.7
        if getattr(settings, "site_logo", False):
            self.img_src = getSiteLogo()
        else:
            # Get the site logo from the static folder
            self.img_src = "%s/%s" % (self.site_url, LOGO_URL)
