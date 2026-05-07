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

import re
from collections import OrderedDict

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.idserver import get_config
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.idserver.idserver import get_alpha_or_number
from senaite.core.idserver.idserver import get_current_year
from senaite.core.idserver.idserver import get_yymmdd
from senaite.core.idserver.idserver import slice as id_slice
from senaite.core.interfaces import INumberGenerator
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implements


class _Placeholder(object):
    """Stand-in for an ID template variable whose value is not yet
    known (e.g. it depends on the content being created). Survives
    `str.format()` by re-emitting itself as a `{name[:spec]}` literal,
    so the rendered next ID still shows the variable's slot.
    """

    def __init__(self, name):
        self.name = name

    def __format__(self, spec):
        if spec:
            return "{" + self.name + ":" + spec + "}"
        return "{" + self.name + "}"


class IIDserverView(Interface):
    """IDServerView
    """


class IDServerView(BrowserView):
    """ This browser view is to house ID Server related functions
    """
    implements(IIDserverView)
    template = ViewPageTemplateFile("templates/numbergenerator.pt")

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        self.portal = api.get_portal()
        self.request.set("disable_plone.rightcolumn", 1)
        self.request.set("disable_border", 1)

        # Handle form submit
        form = self.request.form
        submitted = form.get("submitted", False)

        # nothing to do here
        if not submitted:
            return self.template()

        # Handle "Seed" action
        if form.get("seed", False):
            self._apply_seeds(form.get("seeds", {}))

        return self.template()

    def _apply_seeds(self, seeds):
        """Apply submitted seed values to the number generator storage,
        consolidating per-key outcomes into a single status message
        per category (updated, removed, invalid). Keys whose value
        did not change are skipped silently.
        """
        updated = []
        removed = []
        invalid = []
        for key, raw in seeds.items():
            value = api.to_int(raw, None)
            if value is None:
                invalid.append(key)
                continue
            current = self.storage.get(key)
            if value == 0:
                if current is None:
                    # already absent, nothing to do
                    continue
                del self.storage[key]
                removed.append(key)
            else:
                if current == value:
                    # unchanged
                    continue
                self.set_seed(key, value)
                updated.append((key, value))

        if updated:
            details = ", ".join(
                "{} = {}".format(k, v) for k, v in updated)
            self.add_status_message(
                _("Updated {} key(s): {}").format(len(updated), details),
                "info")
        if removed:
            self.add_status_message(
                _("Removed {} key(s): {}").format(
                    len(removed), ", ".join(removed)),
                "info")
        if invalid:
            self.add_status_message(
                _("Could not convert {} value(s) to integer: {}").format(
                    len(invalid), ", ".join(invalid)),
                "error")
        if not (updated or removed or invalid):
            self.add_status_message(_("No changes"), "info")

    def get_id_template_for(self, key):
        """Get the ID template configured for the portal type encoded
        in the storage key.
        """
        portal_type = self.get_portal_type_for(key)
        config = get_config(None, portal_type=portal_type)
        return config.get("form", "")

    def get_next_id_for(self, key):
        """Render what the next generated ID would look like for the
        given storage key, without actually issuing one.

        Returns None when the suffix portion of the template uses a
        variable that cannot be resolved from the key alone (e.g. a
        custom IIdServerVariables-injected variable).
        """
        portal_type = self.get_portal_type_for(key)
        config = get_config(None, portal_type=portal_type)
        template = config.get("form", "")
        if not template:
            return None

        split_length = config.get("split_length", 1)

        try:
            prefix_template = id_slice(
                template, separator="-", end=split_length)
        except Exception:
            return None
        if not template.startswith(prefix_template):
            return None
        suffix_template = template[len(prefix_template):]

        # Storage key shape: '<portal_type_lower>-<rendered_prefix>'
        portal_type_prefix = portal_type.lower() + "-"
        if not key.startswith(portal_type_prefix):
            return None
        prefix_value = key[len(portal_type_prefix):]

        next_value = self.storage[key] + 1
        # Resolved variables (known from current state)
        variables = {
            "seq": next_value,
            "alpha": get_alpha_or_number(next_value, template),
            "year": get_current_year(),
            "yymmdd": get_yymmdd(),
            # All known counter-like variables share the same next value
            "duplicate_count": next_value,
            "partition_count": next_value,
            "retest_count": next_value,
            "secondary_count": next_value,
            "test_count": next_value,
        }
        # Variables that depend on the upcoming content stay as literal
        # placeholders so the rendered next ID is still readable, e.g.
        # '26-{sampleType}-0042'.
        for name in ("sampleType", "clientId", "parent_ar_id",
                     "parent_base_id", "parent_analysisrequest",
                     "dateSampled", "samplingDate"):
            variables.setdefault(name, _Placeholder(name))

        try:
            suffix = suffix_template.format(**variables)
        except (KeyError, ValueError, IndexError):
            return None

        return prefix_value + suffix

    def get_portal_type_for(self, key):
        """Extract the portal_type segment from a storage key.

        Storage keys look like '<portal_type>-<prefix>'. The
        portal_type is the first dash-separated segment.
        """
        return key.split("-", 1)[0]

    @property
    def friendly_type_labels(self):
        """Mapping of lowercased portal_type -> friendly Title, sourced
        from the portal_types tool (user-friendly types only).

        Storage keys use lowercased portal types, while FTIs are
        registered with their canonical (CamelCase) name. We index by
        lowercase to bridge the two.
        """
        if getattr(self, "_friendly_type_labels", None) is not None:
            return self._friendly_type_labels
        labels = {}
        plone_utils = api.get_tool("plone_utils")
        portal_types = api.get_tool("portal_types")
        for portal_type in plone_utils.getUserFriendlyTypes():
            fti = portal_types.getTypeInfo(portal_type)
            if fti is None:
                continue
            labels[portal_type.lower()] = self.split_camel_case(fti.Title())
        self._friendly_type_labels = labels
        return labels

    def get_label_for(self, portal_type):
        """Return a human-readable label for a portal type segment.
        """
        label = self.friendly_type_labels.get(portal_type.lower())
        if label:
            return label
        return self.split_camel_case(portal_type).title()

    def split_camel_case(self, value):
        """Insert spaces at CamelCase boundaries.

        Handles both 'CamelCase' -> 'Camel Case' and acronym runs like
        'AnalysisCategory' -> 'Analysis Category'.
        """
        if not value:
            return value
        spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", value)
        spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", spaced)
        return spaced

    def get_tab_id_for(self, portal_type):
        """Return a CSS-safe tab id for a portal type."""
        return "tab-{}".format(re.sub(r"[^A-Za-z0-9_-]", "-", portal_type))

    def get_grouped_entries(self):
        """Return storage entries grouped by portal_type.

        Returns an ordered list of dicts:

            [
                {"portal_type": "analysisrequest",
                 "label": "Sample",
                 "tab_id": "tab-analysisrequest",
                 "entries": [{"key": ..., "value": ..., "template": ...},
                             ...]},
                ...
            ]

        Tabs are ordered by descending entry count (most-used first).
        Entries within each tab are sorted descending by key so that
        the most recently created prefixes appear at the top.
        """
        groups = OrderedDict()
        for key in self.storage:
            portal_type = self.get_portal_type_for(key)
            entry = {
                "key": key,
                "value": self.storage[key],
                "template": self.get_id_template_for(key),
                "next_id": self.get_next_id_for(key),
            }
            groups.setdefault(portal_type, []).append(entry)

        # Sort each group's entries: highest key first
        for portal_type, entries in groups.items():
            entries.sort(key=lambda e: e["key"], reverse=True)

        # Build the ordered list of tab descriptors
        # Tabs sorted by entry count descending, then alphabetically
        ordered = sorted(
            groups.items(),
            key=lambda kv: (-len(kv[1]), kv[0]))

        result = []
        for portal_type, entries in ordered:
            result.append({
                "portal_type": portal_type,
                "label": self.get_label_for(portal_type),
                "tab_id": self.get_tab_id_for(portal_type),
                "entries": entries,
                "count": len(entries),
            })
        return result

    @property
    def storage(self):
        number_generator = getUtility(INumberGenerator)
        return number_generator.storage

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def set_seed(self, key, value):
        """Set a number of the number generator
        """
        number_generator = getUtility(INumberGenerator)
        return number_generator.set_number(key, api.to_int(value))

    def seed(self):
        """ Reset the number from which the next generated sequence start.
            If you seed at 100, next seed will be 101
        """
        form = self.request.form
        prefix = form.get("prefix", None)
        if prefix is None:
            return "No prefix provided"
        seed = form.get("seed", None)
        if seed is None:
            return "No seed provided"
        if not seed.isdigit():
            return "Seed must be a digit"
        seed = int(seed)
        if seed < 0:
            return "Seed cannot be negative"

        new_seq = self.set_seed(prefix, seed)
        return 'IDServerView: "%s" seeded to %s' % (prefix, new_seq)
