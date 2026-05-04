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

from bika.lims import api
from plone.app.layout.viewlets.common import GlobalSectionsViewlet as Base
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.vocabularies.hazard_categories import format_title
from senaite.core.vocabularies.hazard_categories import get_category
from senaite.core.vocabularies.hazard_categories import get_overridden_labels
from zope.component import getMultiAdapter

GHS_PICTOGRAM_URL = (
    "{portal_url}/++plone++senaite.core.static/images/ghs/{pictogram}")
W001_PICTOGRAM_URL = (
    "{portal_url}/++plone++senaite.core.static/images/iso/W001.svg")


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

    def hazard_pictograms(self):
        """Return a list of {url, alt, title} for the hazard icons.

        Renders one pictogram per assigned GHS category. When the
        sample is marked hazardous but no category was selected, a
        single ISO 7010 W001 'General warning' pictogram is shown
        as the fallback.
        """
        if not self.is_hazardous():
            return []
        portal_url = api.get_portal().absolute_url()
        codes = list(self.context.getHazardCategories() or [])
        if not codes:
            return [{
                "url": W001_PICTOGRAM_URL.format(portal_url=portal_url),
                "alt": "Hazardous",
                "title": "Hazardous",
            }]
        overrides = get_overridden_labels()
        items = []
        for code in codes:
            category = get_category(code)
            if not category:
                continue
            items.append({
                "url": GHS_PICTOGRAM_URL.format(
                    portal_url=portal_url,
                    pictogram=category["pictogram"]),
                "alt": code,
                "title": format_title(category, overrides),
            })
        return items

    def exclude_invoice(self):
        return self.context.getInvoiceExclude()

    def is_retest(self):
        return self.context.getRetest()
