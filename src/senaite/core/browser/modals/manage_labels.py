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
from bika.lims import senaiteMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.api import label as label_api
from senaite.core.browser.modals import Modal
from senaite.core.config.labels import DEFAULT_LABEL_COLOR
from senaite.core.config.labels import LABEL_COLOR_PRESETS
from senaite.core.config.labels import SAMPLE_LABEL_REINDEX


def _normalize_color(value):
    if not value:
        return u""
    value = api.safe_unicode(value).strip()
    if label_api.is_safe_color(value):
        return value
    return u""


class ManageLabelsModal(Modal):
    """Modal that adds labels to the selected samples.

    Existing labels can be picked from a clickable chip grid; new
    labels can be entered as free text with a color (preset / native
    picker / random). New labels are created in `setup.labels` via
    `senaite.core.api.label.create_label` before assignment.
    """
    template = ViewPageTemplateFile("templates/manage_labels.pt")

    def __call__(self):
        if self.request.form.get("submitted", False):
            return self.handle_submit()
        return self.template()

    def add_status_message(self, message, level="info"):
        return self.context.plone_utils.addPortalMessage(message, level)

    def default_new_label_color(self):
        """Seed value for the new-label color picker."""
        return DEFAULT_LABEL_COLOR

    def get_color_presets(self):
        """Returns `[{name, color}, ...]` for the preset palette."""
        return [{"name": name, "color": color}
                for name, color in LABEL_COLOR_PRESETS]

    def chip_style(self, color):
        """Return a CSS `style` value for a colored chip.

        Built here (not inline in the template) because the CSS
        semicolons would collide with Chameleon's `tal:attributes`
        separator. Returns an empty string for invalid / missing
        colors so chips fall back to the default pill styling.
        """
        return label_api.chip_style(color)

    def swatch_style(self, color):
        if not label_api.is_safe_color(color):
            return u""
        return u"background-color: {c}".format(c=color)

    def get_available_labels(self):
        """Returns `[{name, color}, ...]` for all active labels.
        """
        brains = label_api.query_labels()
        colors = label_api.get_label_colors() or {}
        out = []
        for brain in brains:
            title = api.safe_unicode(brain.Title)
            out.append({
                "name": title,
                "color": colors.get(title, u""),
            })
        return out

    def get_selected_objects(self):
        return [api.get_object(uid) for uid in self.uids]

    def get_shared_labels(self):
        objects = self.get_selected_objects()
        if not objects:
            return []
        shared = set(label_api.get_obj_labels(objects[0]))
        for obj in objects[1:]:
            shared &= set(label_api.get_obj_labels(obj))
        return sorted(shared)

    def get_union_labels(self):
        """Labels currently set on at least one of the selected objects.

        Toggling these in the chip grid lets the user remove them; any
        chip that the user leaves un-selected is interpreted as
        "should not be on the samples after submit".
        """
        union = set()
        for obj in self.get_selected_objects():
            union.update(label_api.get_obj_labels(obj))
        return sorted(union)

    def _parse_selected_labels(self):
        raw = self.request.form.get("selected_labels", "")
        return label_api.parse_label_csv(raw)

    def _parse_initial_labels(self):
        raw = self.request.form.get("initial_labels", "")
        return label_api.parse_label_csv(raw)

    def _parse_new_label(self):
        raw = self.request.form.get("new_label", u"") or u""
        # Coerce to unicode so downstream `get_label_by_name` /
        # `create_label` queries hit the setup catalog's unicode
        # title index without a `UnicodeDecodeError`.
        name = api.safe_unicode(raw).strip()
        color = _normalize_color(self.request.form.get("new_label_color"))
        return name, color

    def handle_submit(self):
        selected = set(self._parse_selected_labels())
        initial = set(self._parse_initial_labels())
        new_name, new_color = self._parse_new_label()

        # Build the final desired set: selected ones the user kept,
        # plus the new free-text label if any.
        if new_name:
            existing = label_api.get_label_by_name(new_name)
            if existing is None:
                kwargs = {}
                if new_color:
                    kwargs["color"] = new_color
                label_api.create_label(new_name, **kwargs)
            elif new_color:
                if getattr(existing, "color", None) != new_color:
                    existing.color = new_color
                    existing.reindexObject()
            selected.add(new_name)

        # Diff against the initial state to derive add/remove sets.
        to_add = sorted(selected - initial)
        to_remove = sorted(initial - selected)

        if not self.uids or (not to_add and not to_remove):
            return self.template()

        affected = 0
        for obj in self.get_selected_objects():
            if to_remove:
                label_api.del_obj_labels(obj, to_remove)
            if to_add:
                label_api.add_obj_labels(obj, to_add)
            obj.reindexObject(idxs=SAMPLE_LABEL_REINDEX)
            affected += 1

        if to_add and to_remove:
            message = _(
                u"labels_changed",
                default=u"Applied ${added} added and ${removed} "
                        u"removed across ${affected} sample(s)",
                mapping={
                    "added": len(to_add),
                    "removed": len(to_remove),
                    "affected": affected,
                },
            )
        elif to_add:
            message = _(
                u"labels_added",
                default=u"Added ${count} label(s) to ${affected} sample(s)",
                mapping={
                    "count": len(to_add),
                    "affected": affected,
                },
            )
        else:
            message = _(
                u"labels_removed",
                default=u"Removed ${count} label(s) from ${affected} sample(s)",
                mapping={
                    "count": len(to_remove),
                    "affected": affected,
                },
            )
        self.add_status_message(message)
        return self.template()
