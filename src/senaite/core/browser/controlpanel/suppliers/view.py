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

import collections

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link_for
from bika.lims.utils import get_email_link
from bika.lims.utils import get_phone_link
from senaite.core.i18n import translate
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.permissions import AddSupplier


class SuppliersView(ListingView):

    def __init__(self, context, request):
        super(SuppliersView, self).__init__(context, request)

        self.catalog = SETUP_CATALOG

        self.contentFilter = {
            "portal_type": "Supplier",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            },
        }

        self.context_actions = {
            _("listing_suppliers_action_add", default="Add"): {
                "url": "++add++Supplier",
                "permission": AddSupplier,
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.title = translate(_(
            "listing_suppliers_title",
            default="Suppliers")
        )
        self.icon = api.get_icon("Suppliers", html_tag=False)
        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("Name", {
                "title": _(
                    u"listing_suppliers_column_name",
                    default=u"Name",
                ),
                "index": "sortable_title",
            }),
            ("Email", {
                "title": _(
                    u"listing_suppliers_column_email",
                    default=u"Email"
                ),
                "toggle": True,
            }),
            ("Phone", {
                "title": _(
                    u"listing_suppliers_column_phone",
                    default=u"Phone"
                ),
                "toggle": True,
            }),
            ("Fax", {
                "title": _(
                    u"listing_suppliers_column_fax",
                    default=u"Fax"
                ),
                "toggle": True,
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_suppliers_state_active",
                    default=u"Active"
                ),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _(
                    u"listing_suppliers_state_inactive",
                    default=u"Inactive"
                ),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _(
                    u"listing_suppliers_state_all",
                    default=u"All"
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        email = obj.getEmail()
        phone = obj.getPhone()

        item["Name"] = api.get_title(obj)
        item["Fax"] = obj.getFax()
        item["Email"] = email
        item["Phone"] = phone

        item["replace"]["Name"] = get_link_for(obj)
        item["replace"]["Email"] = get_email_link(email)
        item["replace"]["Phone"] = get_phone_link(phone)

        return item
