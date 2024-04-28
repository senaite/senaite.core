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

from bika.lims import api
from senaite.core.i18n import translate as t
from plone.memoize.instance import memoize
from plone.memoize.view import memoize_contextless
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.p3compat import cmp
from zope.component import getMultiAdapter


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
    @memoize
    def bootstrap(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="bootstrapview")

    @property
    def portal(self):
        """Returns the Portal Object
        """
        return api.get_portal()

    @property
    def setup(self):
        """Returns the old Setup Object
        """
        return api.get_setup()

    @property
    def senaite_setup(self):
        """Returns the new Setup Object
        """
        return api.get_senaite_setup()

    @memoize_contextless
    def get_icon_for(self, brain, **kw):
        """Returns the icon URL for the given catalog brain
        """
        return self.bootstrap.get_icon_for(brain, **kw)

    @memoize_contextless
    def get_allowed_content_types(self, obj):
        """Get the allowed content types
        """
        portal_types = api.get_tool("portal_types")
        fti = portal_types.getTypeInfo(api.get_portal_type(obj))
        allowed_types = fti.allowed_content_types
        if len(allowed_types) != 1:
            return None
        # convert from unicode -> str for api.search catalog lookup
        return list(map(str, allowed_types))

    def get_count(self, obj):
        """Retrieve the count of contained items
        """
        contained_types = self.get_allowed_content_types(obj)

        # fallback
        if contained_types is None:
            return len(obj.objectIds())

        query = {
            "portal_type": contained_types,
            "is_active": True,
            "path": {
                "query": api.get_path(obj),
                "level": 0,
            }
        }
        brains = api.search(query)
        return len(brains)

    def setupitems(self):
        """Lookup available setup items

        :returns: objects
        """
        items = self.setup.objectValues() + self.senaite_setup.objectValues()

        # sort by (translated) title
        def cmp_by_translated_title(obj1, obj2):
            title1 = t(api.get_title(obj1))
            title2 = t(api.get_title(obj2))
            return cmp(title1, title2)

        return sorted(items, cmp=cmp_by_translated_title)
