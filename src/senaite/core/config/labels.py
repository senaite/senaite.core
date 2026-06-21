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

# Annotation key holding the tuple of assigned label names on a
# labeled object. Set / read via senaite.core.api.label.
LABEL_STORAGE = "senaite.core.labels"

# Annotation key on a Label content item carrying the last-known
# title. Read by the rename-cascade subscriber to detect title
# changes and rewrite stored names across all labeled objects.
PREVIOUS_TITLE_KEY = "senaite.core.label.previous_title"

# Catalog index name re-fetched on every label add / remove so
# listings, the click-to-filter URL and the saved-filter presets
# see the change in the same transaction.
SAMPLE_LABEL_REINDEX = ["labels"]

# Default color seeded into the Manage Labels modal's color picker
# when the user types a new free-text label. SENAITE blue accent.
DEFAULT_LABEL_COLOR = u"#0d6efd"

# Curated preset palette for the Manage Labels modal's color picker.
# Mid-saturation values picked so white chip text stays readable.
# Names are i18n-stable English keys used as preset button tooltips.
LABEL_COLOR_PRESETS = [
    ("Red", u"#d33a3a"),
    ("Orange", u"#e8852b"),
    ("Yellow", u"#d4a017"),
    ("Green", u"#2f9e44"),
    ("Teal", u"#0d9488"),
    ("Blue", u"#0d6efd"),
    ("Purple", u"#7c3aed"),
    ("Pink", u"#db2777"),
    ("Slate", u"#475569"),
]
