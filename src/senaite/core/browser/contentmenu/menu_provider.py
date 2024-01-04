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

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.decorators import readonly_transaction
from zope.component import getMultiAdapter
from zope.interface import implementer

from .interfaces import IMenuProvider


@implementer(IMenuProvider)
class MenuProviderView(BrowserView):
    """View to render a menu/submenu
    """
    template = ViewPageTemplateFile('templates/contentmenu.pt')

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.menu = []

    @property
    def contentmenu(self):
        return getMultiAdapter(
            (self.context, self.request, self), name="plone.contentmenu")

    def available(self):
        return self.contentmenu.available()

    @readonly_transaction
    def workflow_menu(self):
        menu_id = "content_status_history"
        menu = self.contentmenu.menu()
        self.menu = filter(
            lambda m: m.get("action").endswith(menu_id), menu)
        return self.template()
