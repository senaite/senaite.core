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
from senaite.core import logger
from senaite.core.api import label as label_api
from senaite.core.catalog import LABEL_CATALOG
from zope.annotation.interfaces import IAnnotations


# Annotation key used to stash the current title while the Label
# edit form is open. The on_label_modified subscriber reads this on
# save and cascades a rename to every labeled content.
ANNOTATION_OLD_TITLE = "senaite.core.label.pre_edit_title"


def on_label_edit_begun(label, event):
    """Snapshot the Label's current title onto the request.

    Fires when the edit form for a Label is opened (DX
    IEditBegunEvent). The post-save handler `on_label_modified`
    needs this snapshot to detect a rename — by the time
    `IObjectModifiedEvent` reaches us, the form has already written
    the new title and Plone's `IObjectModifiedEvent.descriptions`
    do not carry old values.
    """
    request = _safe_request(label)
    if request is None:
        return
    IAnnotations(request)[ANNOTATION_OLD_TITLE] = api.safe_unicode(
        label.title or u"")


def on_label_modified(label, event):
    """Cascade a Label title rename across every labeled content.

    Reads the pre-edit snapshot left by `on_label_edit_begun`. If
    the title actually changed, walks the label catalog
    (`senaite_catalog_label` only indexes objects providing
    `IHaveLabels`) and rewrites the stored name on each, then
    reindexes the `labels` index so listings, filters and the
    color map see the rename immediately.

    Edits not driven by the form (REST, scripts) do not fire
    `IEditBegunEvent`, so the snapshot is absent and the cascade
    is skipped. Such callers are expected to keep storage and
    title in sync themselves.
    """
    request = _safe_request(label)
    if request is None:
        return
    old_title = IAnnotations(request).pop(ANNOTATION_OLD_TITLE, None)
    new_title = api.safe_unicode(label.title or u"")
    if not old_title or old_title == new_title:
        return

    affected = _rename_label_in_storage(old_title, new_title)
    if affected:
        logger.info(
            "Label rename '{}' -> '{}': updated {} content(s)".format(
                old_title.encode("utf-8"),
                new_title.encode("utf-8"),
                affected,
            )
        )


def _safe_request(label):
    return getattr(label, "REQUEST", None)


def _rename_label_in_storage(old_title, new_title):
    """Walk every labeled object and rewrite `old_title` -> `new_title`.

    Returns the number of objects updated. When `new_title` is
    already present on an object (merge case), the old entry is
    dropped rather than duplicated.
    """
    catalog = api.get_tool(LABEL_CATALOG)
    brains = catalog(labels=old_title)
    affected = 0
    for brain in brains:
        obj = api.get_object(brain, default=None)
        if obj is None:
            continue
        labels = list(label_api.get_obj_labels(obj))
        try:
            index = labels.index(old_title)
        except ValueError:
            # Catalog brain stale; nothing to do here.
            continue
        if new_title in labels:
            labels.pop(index)
        else:
            labels[index] = new_title
        label_api.set_obj_labels(obj, labels)
        obj.reindexObject(idxs=["labels"])
        affected += 1
    return affected
