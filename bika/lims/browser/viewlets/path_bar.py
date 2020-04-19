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
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IClientFolder


class PathBarViewlet(Base):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.path_bar.pt")

    def update(self):
        super(PathBarViewlet, self).update()

        # If current user is a Client, hide Clients folder from breadcrumbs
        user = api.get_current_user()
        client_folder = self.get_client_folder()
        if "Client" in user.getRoles() and client_folder:
            skip = api.get_title(client_folder)
            self.breadcrumbs = filter(lambda b: b.get("Title") not in skip,
                                      self.breadcrumbs)

        # Objects from inside Client folder are always stored directly, w/o
        # subfolders, making it difficult for user to know if what is looking at
        # is a Sample, a Batch or a Contact. Append the name of the portal type
        if IClient.providedBy(self.context.aq_parent):
            title = self.get_portal_type_title()
            if title:
                last = self.breadcrumbs[-1]
                last.update({
                    "Title": "{} ({})".format(last.get("Title", ""), _(title))
                })

    def get_client_folder(self, obj=None):
        """Returns the client folder from the hierarchy, if any. Otherwise,
        returns None
        """
        if not obj:
            obj = self.context
        if api.is_portal(obj):
            return None
        if IClientFolder.providedBy(obj):
            return obj
        parent = api.get_parent(obj)
        return self.get_client_folder(parent)

    def get_portal_type_title(self):
        """Returns the title of the portal type of the current context
        """
        portal = api.get_portal()
        portal_type = api.get_portal_type(self.context)
        portal_type = portal.portal_types.getTypeInfo(portal_type)
        if portal_type:
            return portal_type.title
        return None
