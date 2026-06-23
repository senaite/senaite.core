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

from cgi import escape as html_escape
from urlparse import parse_qs

from bika.lims import api
from bika.lims.api.security import check_permission
from plone.memoize import view
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.utils import safe_unicode
from senaite.app.listing import ListingView as BaseListingView
from senaite.core.api import label as label_api
from senaite.core.permissions import ManageLabels
from senaite.core.permissions import ViewLabels

LABEL_INDEX = "labels"
LABEL_COLUMN = "getLabels"
PRIMARY_COLUMN_CANDIDATES = ("Title", "title", "Name", "name", "getId")


def _read_labels(obj):
    """Return labels for the given brain/object without unnecessary wake.

    Prefers the `getLabels` brain metadata column when present;
    otherwise falls back to waking the object and calling
    `getLabels()`.
    """
    value = getattr(obj, LABEL_COLUMN, None)
    if value is not None:
        # brain metadata is the bare value; never a method here
        return value or ()
    live = api.get_object(obj, default=None)
    if live is None:
        return ()
    if hasattr(live, "getLabels"):
        return live.getLabels() or ()
    return ()


class ListingView(BaseListingView):
    """Base listing view for SENAITE.

    Adds a pencil icon (visible on row hover) to the primary column for
    users with ModifyPortalContent permission. Clicking it opens the
    object's edit form inside a Bootstrap modal showing only the edit
    form content (#content or #content-core).

    Subclasses may set `edit_icon_column` to the column key that should
    receive the icon. When not set, the first non-empty key among
    `("Title", "title", "getId")` is used.

    Subclasses may set `edit_view` to control which view is opened:
    - `"edit"` (default) — appends `/edit` to the object URL; the modal
      auto-closes when the form navigates away after save/cancel.
    - `""` — opens the object's base URL (e.g. the SENAITE sample view
      with inline editing); the modal stays open until dismissed manually.

    Label chips are rendered under the primary column automatically when
    the listing's catalog carries a `labels` KeywordIndex and a
    `getLabels` metadata column. Subclasses may override
    `label_target_column` to pin chips to a specific column.
    """

    edit_icon_column = None
    edit_view = "edit"

    # Column key that receives label chips. `None` resolves to the first
    # non-empty key among `PRIMARY_COLUMN_CANDIDATES`.
    label_target_column = None

    def folderitems(self):
        items = super(ListingView, self).folderitems()
        if not check_permission(ModifyPortalContent, self.context):
            return items
        return [self._add_iframe_edit_link(item) for item in items]

    def before_render(self):
        super(ListingView, self).before_render()
        if self.labels_filterable():
            labels = self.get_request_labels()
            if labels:
                self.contentFilter["labels"] = {
                    "query": labels,
                    "operator": "and",
                }

    def folderitem(self, obj, item, index):
        item = super(ListingView, self).folderitem(obj, item, index)
        if not item:
            return item
        if self.labels_visible():
            self._attach_label_chips(obj, item)
        return item

    # ------------------------------------------------------------------
    # Label support
    # ------------------------------------------------------------------

    @view.memoize
    def labels_visible(self):
        """Whether this listing renders label chips.

        Gated by the `ViewLabels` permission so that client users do
        not see internal lab labels on shared samples. Transposed
        listings (e.g. worksheet manage view) are also skipped because
        their `after` slot is not a sample identifier.
        """
        if getattr(self, "transposed_view", False):
            return False
        return self.can_view_labels()

    @view.memoize
    def can_view_labels(self):
        return check_permission(ViewLabels, self.context)

    @view.memoize
    def labels_filterable(self):
        """Whether chips link to the `?labels=` filter.

        Requires the listing's catalog to carry a `labels` index
        AND the current user to have `ViewLabels`.
        """
        if not self.can_view_labels():
            return False
        catalog_id = getattr(self, "catalog", None)
        if not catalog_id:
            return False
        catalog = api.get_tool(catalog_id, default=None)
        if catalog is None:
            return False
        return LABEL_INDEX in catalog.indexes()

    @view.memoize
    def can_manage_labels(self):
        return check_permission(ManageLabels, self.context)

    def get_request_labels(self):
        """Parse the `labels` query string into a sorted unique list.

        Reads `request.form` first (initial page render) and falls
        back to parsing `QUERY_STRING` directly because the AJAX
        subpath POST (`/view/folderitems`) carries the query in
        `QUERY_STRING` but Zope's publisher does not populate
        `request.form` for the subpath JSON request.
        """
        raw = self.request.form.get("labels")
        if not raw:
            qs = self.request.get("QUERY_STRING") or ""
            raw = parse_qs(qs).get("labels", [])
        return label_api.parse_label_csv(raw)

    def get_label_target_column(self, item):
        if self.label_target_column:
            return self.label_target_column
        for key in PRIMARY_COLUMN_CANDIDATES:
            if key in self.columns:
                return key
        return None

    def render_label_chips(self, obj):
        """Render the inline chip block for the given brain/object.

        Every interpolated value is HTML-escaped before being
        concatenated. Label titles are free-text content on the Label
        type and the brain `color` value is admin-supplied, so both
        must be treated as untrusted in this context — color values
        pass through `is_safe_color` before any inline style is built.

        Chips render as plain `<span>` when the listing's catalog
        does not support label filtering (no `labels` index); as
        clickable filter chips (`is-filterable` class, navigation
        wired client-side) otherwise. Label removal is done through
        the manage-labels modal, so the chip body carries no `×`.
        """
        labels = _read_labels(obj)
        if not labels:
            return u""

        filterable = self.labels_filterable()
        active = set(self.get_request_labels()) if filterable else set()
        uid_attr = self._chip_uid_attr(obj)
        colors = self._get_label_colors_map()

        chips = [
            self._render_chip(label, colors.get(safe_unicode(label)),
                              active, filterable)
            for label in labels
        ]
        return (
            u'<div class="sample-labels" data-uid="{uid}">{chips}</div>'
        ).format(uid=uid_attr, chips=u"".join(chips))

    def _chip_uid_attr(self, obj):
        uid = getattr(obj, "UID", None)
        if callable(uid):
            uid = uid()
        return html_escape(safe_unicode(uid or u""), quote=True)

    def _render_chip(self, label, color, active_set, filterable):
        label_u = safe_unicode(label)
        label_attr = html_escape(label_u, quote=True)
        label_text = html_escape(label_u)
        css_classes = [u"sample-label"]
        if label in active_set:
            css_classes.append(u"active")
        if filterable:
            css_classes.append(u"is-filterable")
        style = label_api.chip_style(color)
        style_attr = u' style="{}"'.format(style) if style else u""
        return (
            u'<span class="{cls}" data-label="{label_attr}"{style}>'
            u'<span class="sample-label-text">{label_text}</span>'
            u'</span>'
        ).format(
            cls=u" ".join(css_classes),
            label_attr=label_attr,
            label_text=label_text,
            style=style_attr,
        )

    @view.memoize
    def _get_label_colors_map(self):
        """Per-render cache of `{label_name: color}` from the setup catalog.
        """
        return label_api.get_label_colors()

    def _attach_label_chips(self, obj, item):
        """Stack chips under the primary column value.

        Going through `replace` avoids the `<span class="after-item">`
        wrapper used by the `after` slot, which forces inline flow
        and prevents chips from breaking to a new line.

        Pre-existing `replace[target]` content (e.g. a `<a href=…>`
        link the consumer view installed) is trusted as HTML. When
        there is no such entry, the raw cell value comes from the
        catalog metadata column and is escaped before being inlined,
        so a sample id containing `<` cannot inject markup.
        """
        target = self.get_label_target_column(item)
        if not target:
            return
        chips = self.render_label_chips(obj)
        if not chips:
            return
        replace_map = item.setdefault("replace", {})
        existing_html = replace_map.get(target)
        if existing_html is None:
            raw_value = safe_unicode(item.get(target, u"") or u"")
            existing_html = html_escape(raw_value)
        replace_map[target] = (
            u'<div class="sample-id-with-labels">'
            u'<div class="sample-id-with-labels__value">{value}</div>'
            u'{chips}'
            u'</div>'
        ).format(value=safe_unicode(existing_html), chips=chips)

    # ------------------------------------------------------------------
    # Edit icon
    # ------------------------------------------------------------------

    def _get_edit_icon_column(self, item):
        """Return the column key to attach the edit icon to."""
        if self.edit_icon_column:
            return self.edit_icon_column
        for key in PRIMARY_COLUMN_CANDIDATES:
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
        # Prepend to any existing "after" content (e.g. accredited icons).
        # Wrap with safe_unicode: get_image() returns byte strings that would
        # cause UnicodeDecodeError when concatenated with the unicode icon.
        existing = safe_unicode(item.get("after", {}).get(col, u""))
        item["after"][col] = icon + existing
        return item
