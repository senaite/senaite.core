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
from bika.lims.utils import get_link
from senaite.core.browser.clients.client.contacts.view import \
    ClientContactsView


class ContactsView(ClientContactsView):
    """Global Contacts listing view showing all system contacts
    """

    def __init__(self, context, request):
        super(ContactsView, self).__init__(context, request)

        self.contentFilter = {
            "portal_type": "Contact",
            "sort_on": "sortable_title",
        }

        global_contacts_path = "/".join(self.context.getPhysicalPath())

        # Override the content filter based on the cookie
        if self.include_client_contacts:
            self.contentFilter.pop("path", None)
        else:
            # Show only global contacts
            self.contentFilter = {
                "portal_type": "Contact",
                "sort_on": "sortable_title",
                "path": {"query": global_contacts_path, "level": 0}
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

        for review_state in self.review_states:
            # ensure all columns are included
            review_state["columns"] = self.columns.keys()
            if self.include_client_contacts:
                # remove the path query
                review_state["contentFilter"].pop("path", None)
            else:
                # add the path query
                review_state["contentFilter"]["path"] = {
                    "query": global_contacts_path,
                    "level": 0
                }

    def update(self):
        """Update hook
        """
        super(ContactsView, self).update()

    @property
    def include_client_contacts(self):
        """Returns if client contacts should be included or not
        """
        return self.request.cookies.get("include_client_contacts", "") == "1"

    def folderitem(self, obj, item, index):
        """Augment folder item with Location information
        """
        item = super(ContactsView, self).folderitem(obj, item, index)

        # Get the contact object
        contact = api.get_object(obj)
        parent = api.get_parent(contact)

        # Set the parent location (either Client or global)
        location = parent.Title()
        item["Location"] = location

        # Make the location a clickable link
        parent_url = api.get_url(parent)
        item["replace"]["Location"] = get_link(parent_url, location)

        return item
