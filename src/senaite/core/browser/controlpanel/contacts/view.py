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

from senaite.core.browser.clients.client.contacts.view import ClientContactsView


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
