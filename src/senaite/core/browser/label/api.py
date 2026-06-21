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

from bika.lims import api
from bika.lims.api.security import check_permission
from bika.lims.decorators import returns_json
from Products.Five.browser import BrowserView
from senaite.core.api import label as label_api
from senaite.core.config.labels import SAMPLE_LABEL_REINDEX
from senaite.core.permissions import ManageLabels
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class LabelsAPI(BrowserView):
    """JSON endpoint for label management.

    Routes are dispatched via subpath traversal:

    - `<context>/@@labels/add` — POST: add one or more labels to
      the context object. Auto-creates the corresponding `Label`
      in `setup.labels` when the name is new. Requires
      `senaite.core: Manage Labels`.

    - `<context>/@@labels/remove` — POST: remove one or more
      labels from the context object. Requires
      `senaite.core: Manage Labels`.

    - `@@labels/available` — GET: returns `{name, color,
      description}` for every active label so consumers (e.g. the
      active-filter chips above the listing search box) can paint
      chips in the matching color. Requires `senaite.core: View
      Labels`.

    The browser page is registered at the lowest of the two
    permissions (`ViewLabels`); the write routes re-check
    `ManageLabels` and return 403 when missing. This keeps the
    JSON contract symmetric (every route returns a JSON body) and
    avoids exposing two ZCML page registrations for what is
    logically one endpoint.

    Labels are accepted in either of the two request shapes that
    HTTP can deliver: `label=foo&label=bar` (repeated key) or
    `labels=foo,bar` (comma-separated). Both are parsed through
    `senaite.core.api.label.parse_label_csv`.
    """

    def __init__(self, context, request):
        super(LabelsAPI, self).__init__(context, request)
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        self.traverse_subpath.append(name)
        return self

    def __call__(self):
        if len(self.traverse_subpath) != 1:
            return self._not_found()
        route = self.traverse_subpath[0]
        handler = getattr(self, "_route_{}".format(route), None)
        if handler is None:
            return self._not_found()
        return handler()

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @returns_json
    def _route_add(self):
        if not check_permission(ManageLabels, self.context):
            return self._forbidden()
        labels = self._read_submitted_labels()
        if not labels:
            return self._empty_input()
        for name in labels:
            if label_api.get_label_by_name(name) is None:
                label_api.create_label(name)
        new_labels = label_api.add_obj_labels(self.context, labels)
        self.context.reindexObject(idxs=SAMPLE_LABEL_REINDEX)
        return {"success": True, "labels": list(new_labels)}

    @returns_json
    def _route_remove(self):
        if not check_permission(ManageLabels, self.context):
            return self._forbidden()
        labels = self._read_submitted_labels()
        if not labels:
            return self._empty_input()
        new_labels = label_api.del_obj_labels(self.context, labels)
        self.context.reindexObject(idxs=SAMPLE_LABEL_REINDEX)
        return {"success": True, "labels": list(new_labels)}

    @returns_json
    def _route_available(self):
        brains = label_api.query_labels()
        labels = []
        for brain in brains:
            # Prefer the `getColor` metadata column. Falls back to
            # waking the Label and reading the live attribute when
            # the catalog rebuild has not yet propagated the new
            # column to existing brains (matches the fallback in
            # `senaite.core.api.label.get_label_colors`).
            color = getattr(brain, "getColor", u"") or u""
            if not color:
                obj = api.get_object(brain, default=None)
                if obj is not None:
                    color = getattr(obj, "color", u"") or u""
            labels.append({
                "name": api.safe_unicode(brain.Title),
                "color": api.safe_unicode(color),
                "description": api.safe_unicode(brain.Description or u""),
            })
        return {"labels": labels}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _read_submitted_labels(self):
        """Parse labels from the request form into a sorted unique list.

        Accepts both `label=foo&label=bar` (repeated keys) and
        `labels=foo,bar` (comma-separated) shapes; both go through
        the same parser to return unicode names.
        """
        values = []
        single = self.request.form.get("label")
        if isinstance(single, (list, tuple)):
            values.extend(single)
        elif single:
            values.append(single)
        multi = self.request.form.get("labels")
        if multi:
            values.append(multi)
        return label_api.parse_label_csv(values)

    @returns_json
    def _empty_input(self):
        self.request.response.setStatus(400)
        return {
            "success": False,
            "error": "No labels submitted",
            "labels": list(label_api.get_obj_labels(self.context)),
        }

    @returns_json
    def _forbidden(self):
        self.request.response.setStatus(403)
        return {"success": False, "error": "Forbidden"}

    @returns_json
    def _not_found(self):
        self.request.response.setStatus(404)
        return {
            "success": False,
            "error": "Unknown route. Use one of: add, remove, available",
        }
