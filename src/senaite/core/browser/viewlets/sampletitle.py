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

from plone.app.layout.viewlets.common import GlobalSectionsViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter


class SampleTitleViewlet(Base):
    index = ViewPageTemplateFile("templates/sampletitle.pt")

    def __init__(self, context, request, view, manager=None):
        super(SampleTitleViewlet, self).__init__(
            context, request, view, manager=manager)

    @property
    @memoize
    def theme_view(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="senaite_theme")

    def update(self):
        super(SampleTitleViewlet, self).update()

    def is_hazardous(self):
        return self.context.getHazardous()

    def exclude_invoice(self):
        return self.context.getInvoiceExclude()

    def is_retest(self):
        return self.context.getRetest()
