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

import json

from bika.lims import api
from Products.Five.browser import BrowserView
from senaite.core.api import label as label_api


SAMPLE_LABEL_REINDEX = ["labels"]


def _parse_labels(request):
    """Return the labels submitted with the request as a sorted list.

    Accepts both `label=foo&label=bar` and `labels=foo,bar` forms.
    """
    values = []
    single = request.form.get("label")
    if isinstance(single, (list, tuple)):
        values.extend(single)
    elif single:
        values.append(single)
    multi = request.form.get("labels")
    if multi:
        values.append(multi)
    return label_api.parse_label_csv(values)


def _json_response(request, payload):
    request.response.setHeader("Content-Type", "application/json")
    return json.dumps(payload)


class AddLabelView(BrowserView):
    """POST endpoint that adds one or more labels to the context.

    Free-text labels are accepted: a submitted name that does not match
    an existing `Label` in `setup.labels` is created on the fly.
    Protected by the `senaite.core: Manage Labels` permission via ZCML.
    """

    def __call__(self):
        labels = _parse_labels(self.request)
        if not labels:
            return _json_response(self.request, {
                "success": False,
                "error": "No labels submitted",
                "labels": list(label_api.get_obj_labels(self.context)),
            })

        for name in labels:
            if label_api.get_label_by_name(name) is None:
                label_api.create_label(name)

        new_labels = label_api.add_obj_labels(self.context, labels)
        self.context.reindexObject(idxs=SAMPLE_LABEL_REINDEX)
        return _json_response(self.request, {
            "success": True,
            "labels": list(new_labels),
        })


class RemoveLabelView(BrowserView):
    """POST endpoint that removes one or more labels from the context.

    Protected by the `senaite.core: Manage Labels` permission via ZCML.
    """

    def __call__(self):
        labels = _parse_labels(self.request)
        if not labels:
            return _json_response(self.request, {
                "success": False,
                "error": "No labels submitted",
                "labels": list(label_api.get_obj_labels(self.context)),
            })

        new_labels = label_api.del_obj_labels(self.context, labels)
        self.context.reindexObject(idxs=SAMPLE_LABEL_REINDEX)
        return _json_response(self.request, {
            "success": True,
            "labels": list(new_labels),
        })


class AvailableLabelsView(BrowserView):
    """GET endpoint returning all active labels as JSON.

    Returns name, color and description for every label so the listing
    can render chip colors consistently. Available to any authenticated
    user (chip coloring is read-only and consumed both by the
    chip-color sync on the page header and by the inline label picker).
    """

    def __call__(self):
        brains = label_api.query_labels()
        labels = []
        for brain in brains:
            color = getattr(brain, "color", u"") or u""
            labels.append({
                "name": api.safe_unicode(brain.Title),
                "color": api.safe_unicode(color),
                "description": api.safe_unicode(brain.Description or ""),
            })
        return _json_response(self.request, {"labels": labels})
