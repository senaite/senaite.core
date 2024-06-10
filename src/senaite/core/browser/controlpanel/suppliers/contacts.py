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
from bika.lims.utils import get_link
from senaite.core.i18n import translate
from senaite.app.listing import ListingView
from senaite.core.catalog import CONTACT_CATALOG


class ContactsView(ListingView):
    """Supplier Contacts
    """

    def __init__(self, context, request):
        super(ContactsView, self).__init__(context, request)

        self.catalog = CONTACT_CATALOG

        self.contentFilter = {
            "portal_type": "SupplierContact",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0,
            }
        }

        self.context_actions = {
            _("listing_suppliercontacts_action_add", default="Add"): {
                "url": "createObject?type_name=SupplierContact",
                "permission": "Add portal content",
                "icon": "senaite_theme/icon/plus"
            }
        }

        self.title = translate(_(
            "listing_suppliercontacts_title",
            default="Contacts")
        )
        self.icon = api.get_icon("Contact", html_tag=False)
        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("getFullname", {
                "title": _(
                    u"listing_suppliercontacts_column_fullname",
                    default=u"FullName"
                )
            }),
            ("getEmailAddress", {
                "title": _(
                    u"listing_suppliercontacts_column_emailaddress",
                    default=u"Email Address"
                )
            }),
            ("getBusinessPhone", {
                "title": _(
                    u"listing_suppliercontacts_column_businessphone",
                    default=u"Business Phone"
                )
            }),
            ("getMobilePhone", {
                "title": _(
                    u"listing_suppliercontacts_column_mobilephone",
                    default=u"Mobile Phone"
                )
            }),
            ("getFax", {
                "title": _(
                    u"listing_suppliercontacts_column_fax",
                    default=u"Fax"
                )
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _(
                    u"listing_suppliercontacts_state_all",
                    default=u"All"
                ),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        name = obj.getFullname()
        url = obj.absolute_url()

        item["replace"]["getFullname"] = get_link(url, value=name)

        return item
