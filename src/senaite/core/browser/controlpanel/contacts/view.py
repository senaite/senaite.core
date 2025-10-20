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

from collections import OrderedDict

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IClient
from bika.lims.utils import get_link
from senaite.core.browser.clients.client.contacts.view import \
    ClientContactsView


class ContactsView(ClientContactsView):
    """Global Contacts listing view showing all system contacts
    """

    def __init__(self, context, request):
        super(ContactsView, self).__init__(context, request)
        # Override the content filter to show all contacts, not just those in a specific path
        self.contentFilter = {
            "portal_type": "Contact",
            "sort_on": "sortable_title",
        }

        # Add Location column after Full Name
        self.columns = OrderedDict((
            ("getFullname", {
                "title": _("Full Name"),
                "index": "getFullname",
                "sortable": True, }),
            ("Username", {
                "title": _("User Name"), }),
            ("getEmailAddress", {
                "title": _("Email Address"), }),
            ("getBusinessPhone", {
                "title": _("Business Phone"), }),
            ("getMobilePhone", {
                "title": _("MobilePhone"), }),
            ("Location", {
                "title": _("Location"),
                "sortable": False, }),
        ))

        # Update review states to include the Location column
        self.review_states = [
            {"id": "default",
             "title": _("Active"),
             "contentFilter": {"is_active": True},
             "transitions": [{"id": "deactivate"}, ],
             "columns": self.columns.keys()},
            {"id": "inactive",
             "title": _("Inactive"),
             "contentFilter": {"is_active": False},
             "transitions": [{"id": "activate"}, ],
             "columns": self.columns.keys()},
            {"id": "all",
             "title": _("All"),
             "contentFilter": {},
             "columns": self.columns.keys()},
        ]

    def folderitem(self, obj, item, index):
        """Augment folder item with Location information
        """
        item = super(ContactsView, self).folderitem(obj, item, index)

        # Get the contact object
        contact = api.get_object(obj)
        parent = api.get_parent(contact)

        # Determine the location based on parent type
        if IClient.providedBy(parent):
            # Contact is under a client
            location = parent.Title()
        else:
            # Contact is global (under setup/contacts)
            location = parent.Title()

        item["Location"] = location

        # Make the location a clickable link
        parent_url = api.get_url(parent)
        item["replace"]["Location"] = get_link(parent_url, location)

        return item
