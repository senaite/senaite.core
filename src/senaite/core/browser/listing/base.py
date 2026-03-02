# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
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

from bika.lims.api.security import check_permission
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.utils import safe_unicode
from senaite.app.listing import ListingView as BaseListingView


class ListingView(BaseListingView):
    """Base listing view for SENAITE.

    Adds a pencil icon (visible on row hover) to the primary column for
    users with ModifyPortalContent permission. Clicking it opens the
    object's edit form inside a Bootstrap modal showing only the edit
    form content (#content or #content-core).

    Subclasses may set ``edit_icon_column`` to the column key that should
    receive the icon. When not set, the first non-empty key among
    ``("Title", "title", "getId")`` is used.

    Subclasses may set ``edit_view`` to control which view is opened:
    - ``"edit"`` (default) — appends ``/edit`` to the object URL; the modal
      auto-closes when the form navigates away after save/cancel.
    - ``""`` — opens the object's base URL (e.g. the SENAITE sample view
      with inline editing); the modal stays open until dismissed manually.
    """

    edit_icon_column = None
    edit_view = "edit"

    def folderitems(self):
        items = super(ListingView, self).folderitems()
        if not check_permission(ModifyPortalContent, self.context):
            return items
        return [self._add_iframe_edit_link(item) for item in items]

    def _get_edit_icon_column(self, item):
        """Return the column key to attach the edit icon to."""
        if self.edit_icon_column:
            return self.edit_icon_column
        for key in ("Title", "title", "getId"):
            if item.get(key):
                return key
        return None

    def _add_iframe_edit_link(self, item):
        url = safe_unicode(item.get("url", ""))
        col = self._get_edit_icon_column(item)
        title = safe_unicode(item.get(col, "")) if col else u""
        if not url or not title or not col:
            return item
        edit_view = self.edit_view or u""
        edit_url = u"{}/{}".format(url, edit_view).rstrip(u"/") if edit_view \
            else url
        icon = (
            u'<a href="{url}" class="iframe-edit-link iframe-edit-icon"'
            u' data-title="{title}" data-edit-view="{edit_view}" title="Edit">'
            u'<i class="fa fa-pencil"></i>'
            u'</a>'
        ).format(url=edit_url, title=title, edit_view=edit_view)
        # Prepend to any existing "after" content (e.g. accredited icons)
        existing = item.get("after", {}).get(col, u"")
        item["after"][col] = icon + existing
        return item
