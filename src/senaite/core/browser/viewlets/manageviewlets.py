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

from plone.app.viewletmanager.manager import ManageViewlets as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ManageViewlets(Base):
    """SENAITE-specific `@@manage-viewlets` view.

    Behaves like the stock view (each viewlet manager renders its own
    show/hide/reorder box in place, so the managers appear nested and
    positioned exactly as they are on the site), but renders through the
    SENAITE main template and styles the manager/viewlet boxes into clean
    nested boxes (see the accompanying `manage-viewlets.pt`).
    """
    index = ViewPageTemplateFile("templates/manage-viewlets.pt")
