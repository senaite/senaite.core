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

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import PathBarViewlet as Base

from bika.lims import api


class PathBarViewlet(Base):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.path_bar.pt")

    def update(self):
        super(PathBarViewlet, self).update()

        # If current user is a Client, hide Clients folder from breadcrumbs
        user = api.get_current_user()
        if "Client" in user.getRoles():
            skip = api.get_title(api.get_portal().clients)
            self.breadcrumbs = filter(lambda b: b.get("Title") not in skip,
                                      self.breadcrumbs)
