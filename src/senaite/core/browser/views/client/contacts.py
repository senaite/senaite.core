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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from collections import OrderedDict
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link
from bika.lims.utils import get_email_link
from Products.CMFCore.permissions import AddPortalContent
from senaite.app.listing import ListingView


class ClientContactsView(ListingView):
    """Displays a table listing with the available client contacts from current
    context (client)
    """

    def __init__(self, context, request):
        super(ClientContactsView, self).__init__(context, request)

        self.catalog = "portal_catalog"
        self.contentFilter = {
            "portal_type": "ClientContact",
            "sort_on": "sortable_title",
            "path": {
                "query": api.get_path(self.context),
                "level": 0
            }
        }

        self.context_actions = {
            _('Add'): {
                "url": "++add++ClientContact",
                "icon": "++resource++bika.lims.images/add.png",
                "permission": AddPortalContent,
            }}

        t = self.context.translate
        self.title = t(_("Contacts"))
        self.description = t(_(""))

        icon_path = "/++resource++bika.lims.images/client_contact_big.png"
        self.icon = "{}{}".format(self.portal_url, icon_path)

        self.show_select_column = True
        self.pagesize = 50

        self.columns = OrderedDict((
            ("fullname", {
                "title": _("Full Name"),
                "index": "getFullname", }),
            ("username", {
                "title": _("User Name"), }),
            ("email", {
                "title": _("Email Address"), }),
            ("business_phone", {
                "title": _("Business Phone"), }),
            ("mobile_phone", {
                "title": _("MobilePhone"), }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        obj = api.get_object(obj)

        fullname = obj.getFullname()
        email = obj.getEmail()
        item.update({
            "fullname": fullname,
            "username": obj.getUsername(),
            "email": email,
            "business_phone": obj.getBusinessPhone(),
            "mobile_phone": obj.getMobilePhone(),
        })

        url = api.get_url(obj)
        item["replace"].update({
            "fullname": get_link(url, fullname),
            "email": get_email_link(email)
        })

        return item
