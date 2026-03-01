# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from collections import OrderedDict

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.utils import get_link_for
from senaite.core.browser.listing.base import ListingView
from senaite.core.catalog import ATTACHMENTS_CATALOG


class ClientAttachmentsView(ListingView):
    """Listing view for client attachments (SimpleFile/SimpleImage)"""

    def __init__(self, context, request):
        super(ClientAttachmentsView, self).__init__(context, request)
        self.catalog = ATTACHMENTS_CATALOG
        self.contentFilter = {
            "portal_type": ["SimpleFile", "SimpleImage"],
            "path": {
                "query": api.get_path(context),
            },
            "sort_on": "created",
            "sort_order": "descending"
        }
        self.context_actions = {}
        self.show_select_all_checkbox = True
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "client_attachments"
        self.title = "Attachments"
        self.description = "Client attachments and files"

        # Build workflow action delete URL
        view_url = "{}/{}".format(api.get_url(context), self.__name__)
        delete_url = "workflow_action?action=delete&redirect_url={}".format(
            view_url)

        self.columns = OrderedDict((
            ("Title", {
                "title": _("Filename"),
                "index": "getId"
            }),
            ("content_type", {
                "title": _("Type"),
                "index": "content_type"
            }),
            ("get_size", {
                "title": _("Size"),
                "index": "get_size"
            }),
            ("created", {
                "title": _("Created"),
                "index": "created"
            }),
            ("Creator", {
                "title": _("Creator"),
                "index": "Creator"
            }),
            ("Location", {
                "title": _("Location"),
                "index": "path"
            }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "columns":  self.columns.keys(),
                "transitions": [],
                "custom_transitions": [
                    {
                        "id": "delete",
                        "title": _("Delete"),
                        "url": delete_url,
                        "css_class": "btn btn-danger",
                    }
                ]
            }
        ]

    def update(self):
        """Update the view"""
        super(ClientAttachmentsView, self).update()

    def before_render(self):
        """Before render hook"""
        super(ClientAttachmentsView, self).before_render()

    def folderitem(self, obj, item, index):
        """Augment folder item with custom data"""
        item = super(ClientAttachmentsView, self).folderitem(
            obj, item, index)

        # Get the actual object
        attachment = api.get_object(obj)

        # Get the parent container
        container = api.get_parent(attachment)

        # Filename (Title)
        item["Title"] = api.get_title(attachment)

        # Content type (now a property)
        item["content_type"] = attachment.content_type or _("Unknown")

        # File size (formatted)
        item["get_size"] = attachment.get_formatted_size()

        # Created date
        created = api.get_creation_date(attachment)
        item["created"] = self.ulocalized_time(created, long_format=True)

        # Creator
        item["Creator"] = attachment.Creator()

        download_url = self.get_download_url(attachment)
        item["replace"]["Title"] = u"<a href='{}'>{}</a>".format(
            download_url,
            attachment.get_filename()
        )

        # Location
        item["Location"] = api.get_title(container)
        item["replace"]["Location"] = get_link_for(container)

        return item

    def get_download_url(self, obj):
        """Get the download URL for a File or Image object

        :param obj: The File or Image object
        :returns: Download URL string
        """
        url = api.get_url(obj)
        portal_type = api.get_portal_type(obj)

        if portal_type == "SimpleFile":
            return "{}/@@download/file".format(url)
        elif portal_type == "SimpleImage":
            return "{}/@@download/image".format(url)

        # Fallback to object URL
        return url

    def get_transitions(self):
        """Override to remove workflow transitions"""
        return []
