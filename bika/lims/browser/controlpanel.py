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

import os

from bika.lims.utils import t
from plone.app.controlpanel.overview import OverviewControlPanel
from plone.memoize.volatile import cache
from plone.memoize.volatile import store_on_context
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api


def modified_cache_key(method, self, brain_or_object):
    """A cache key that returns the millis of the last modification time
    """
    return api.get_modification_date(brain_or_object).millis()


class SenaiteOverviewControlPanel(OverviewControlPanel):
    """Bootstrapped version of the standard Plone Control Panel
    """
    template = ViewPageTemplateFile(
        "templates/plone.app.controlpanel.overview.pt")


class SetupView(BrowserView):
    """Ordered overview of all Setup Items
    """
    template = ViewPageTemplateFile("templates/setupview.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.request.set("disable_border", 1)
        return self.template()

    @property
    def portal(self):
        """Returns the Portal Object
        """
        return api.get_portal()

    @property
    def setup(self):
        """Returns the Senaite Setup Object
        """
        return api.get_setup()

    @cache(modified_cache_key, store_on_context)
    def get_icon_url(self, brain):
        """Returns the (big) icon URL for the given catalog brain
        """
        icon_url = api.get_icon(brain, html_tag=False)
        url, icon = icon_url.rsplit("/", 1)
        relative_url = url.lstrip(self.portal.absolute_url())
        name, ext = os.path.splitext(icon)

        # big icons endwith _big
        if not name.endswith("_big"):
            icon = "{}_big{}".format(name, ext)

        icon_big_url = "/".join([relative_url, icon])

        # fall back to a default icon if the looked up icon does not exist
        if self.context.restrictedTraverse(icon_big_url, None) is None:
            icon_big_url = "++resource++bika.lims.images/gears.png"

        return icon_big_url

    def setupitems(self):
        """Lookup available setup items

        :returns: catalog brains
        """
        query = {
            "path": {
                "query": api.get_path(self.setup),
                "depth": 1,
            },
        }
        items = api.search(query, "portal_catalog")
        # filter out items
        items = filter(lambda item: not item.exclude_from_nav, items)

        # sort by (translated) title
        def cmp_by_translated_title(brain1, brain2):
            title1 = t(api.get_title(brain1))
            title2 = t(api.get_title(brain2))
            # XXX: Python 3 compatibility
            return cmp(title1, title2)

        return sorted(items, cmp=cmp_by_translated_title)
