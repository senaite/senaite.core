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

from Products.CMFCore.permissions import View
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import PathBarViewlet as Base

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.api.security import check_permission
from bika.lims.interfaces import IClient


class PathBarViewlet(Base):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.path_bar.pt")

    def update(self):
        super(PathBarViewlet, self).update()

        # Hide breadcrumbs for which current user does not have "View" perm
        self.breadcrumbs = self.get_breadcrumbs()

    def get_breadcrumbs(self):
        """Generates the breadcrumbs. Items for which current user does not
        have the View permission granted are omitted
        """
        hierarchy = []
        current = self.context
        while not api.is_portal(current):
            if api.is_object(current):
                if check_permission(View, current):
                    hierarchy.append(current)
            else:
                # Some objects (e.g. portal_registry) are not supported
                hierarchy.append(current)
            current = current.aq_parent
        hierarchy = reversed(hierarchy)
        return map(self.to_breadcrumb, hierarchy)

    def to_breadcrumb(self, obj):
        """Converts the object to a breadcrumb for the template consumption
        """
        return {"Title": self.get_obj_title(obj),
                "absolute_url": self.get_obj_url(obj)}

    def get_obj_title(self, obj):
        """Returns the title of the object to be displayed as breadcrumb
        """
        if not api.is_object(obj):
            # Some objects (e.g. portal_registry) are not supported
            return obj.Title()

        title = api.get_title(obj)
        if IClient.providedBy(obj.aq_parent):
            # Objects from inside Client folder are always stored directly, w/o
            # subfolders, making it difficult for user to know if what is
            # looking at is a Sample, a Batch or a Contact. Append the name of
            # the portal type
            pt_title = self.get_portal_type_title(obj)
            if pt_title:
                title = "{} ({})".format(title, _(pt_title))
        return title

    def get_obj_url(self, obj):
        """Returns the absolute url of the object passed-in
        """
        if not api.is_object(obj):
            # Some objects (e.g. portal_registry) are not supported
            return obj.absolute_url()

        return api.get_url(obj)

    def get_portal_type_title(self, obj):
        """Returns the title of the portal type of the obj passed-in
        """
        portal = api.get_portal()
        portal_type = api.get_portal_type(obj)
        portal_type = portal.portal_types.getTypeInfo(portal_type)
        if portal_type:
            return portal_type.title
        return None
