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

from Products.CMFPlone.controlpanel.browser.quickinstaller import \
    ManageProductsView as BaseView


class ManageProductsView(BaseView):
    """
    """

    def get_available(self):
        """Available add-ons
        """
        available = []
        available_addons = self.get_addons(apply_filter="available").values()
        for addon in available_addons:
            id = addon.get("id")
            if id.startswith("plone."):
                continue
            elif id.startswith("Products."):
                continue
            elif id.startswith("collective."):
                continue
            elif id == "bika.lims":
                continue
            available.append(addon)
        return available
