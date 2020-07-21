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

from bika.lims import api
from bika.lims.api.security import check_permission
from plone.app.layout.viewlets import ViewletBase
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

DEFAULT_PERM = "View"
DEFAULT_ADD_PERM = "Add portal content"
SVG_ADD_ICON = "senaite_theme/icon/plus"


class ListingTableTitleViewlet(ViewletBase):
    """This viewlet inserts the title and context actions
    """
    index = ViewPageTemplateFile("templates/listingtitle.pt")

    def update(self):
        super(ListingTableTitleViewlet, self).update()

    @property
    @memoize
    def boootstrap_view(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="bootstrapview"
        )

    @property
    @memoize
    def icon(self):
        return self.boootstrap_view.get_icon_for(self.context, height="24")

    def title(self):
        return self.view.title or self.context.Title()

    def get_context_actions(self):
        """Get the defined ccontex actions of the listing view
        """
        actions = getattr(self.view, "context_actions", {})
        for k, v in actions.items():
            url = v.get("url")
            if not url:
                continue
            context_url = api.get_url(self.context)
            if not url.startswith(context_url):
                url = "{}/{}".format(context_url, url)
            default_perm = k == "Add" and DEFAULT_ADD_PERM or DEFAULT_PERM
            perm = v.get("permission", default_perm)
            if not check_permission(perm, self.context):
                continue
            icon = v.get("icon")
            if icon.endswith("add.png"):
                icon = SVG_ADD_ICON
            action = v
            action.update({
                "title": k,
                "url": url,
                "permission": perm,
                "icon": icon,
            })
            yield action


class ListingTableDescriptionViewlet(ViewletBase):
    """This viewlet inserts the title and context actions
    """
    index = ViewPageTemplateFile("templates/listingdescription.pt")

    def description(self):
        return self.view.description
