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
from senaite.core.config.labels import PREVIOUS_TITLE_KEY
from senaite.core.config.labels import SAMPLE_LABEL_REINDEX
from zope.annotation.interfaces import IAnnotations


def on_label_added(label, event):
    """Record the initial title as the rename baseline.

    Fires when a `Label` is added to `setup.labels`. We seed the
    persistent annotation here so the first edit can compare against
    a known baseline rather than treating every modification as a
    rename.
    """
    title = api.safe_unicode(label.title or u"")
    IAnnotations(label)[PREVIOUS_TITLE_KEY] = title


def on_label_modified(label, event):
    """Cascade a Label title rename across every labeled content.

    Reads the previous title from the persistent annotation on the
    Label itself. If the title actually changed, walks the label
    catalog (`senaite_catalog_label` only indexes objects providing
    `IHaveLabels`) and rewrites the stored name on each, then
    reindexes the `labels` index so listings, filters and the color
    map see the rename immediately.

    Pre-existing Labels created before the subscriber was installed
    have no annotation yet — the first modification seeds the
    baseline rather than firing a false-positive cascade.
    """
    annotations = IAnnotations(label)
    new_title = api.safe_unicode(label.title or u"")
    old_title = annotations.get(PREVIOUS_TITLE_KEY)

    if old_title is None:
        # First modification after install / first save after upgrade.
        # Seed the baseline; no rename to cascade.
        annotations[PREVIOUS_TITLE_KEY] = new_title
        return

    if old_title == new_title:
        return

    affected = _rename_label_in_storage(old_title, new_title)
    annotations[PREVIOUS_TITLE_KEY] = new_title
    if affected:
        logger.info(
            "Label rename '{}' -> '{}': updated {} content(s)".format(
                old_title.encode("utf-8"),
                new_title.encode("utf-8"),
                affected,
            )
        )


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
        obj.reindexObject(idxs=SAMPLE_LABEL_REINDEX)
        affected += 1
    return affected
