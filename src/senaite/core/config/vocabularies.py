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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import _

SAMPLE_PRESERVATION_CATEGORIES = (
    ("field", _(
        u"sample_preservation_category_vocab_field",
        default=u"Field Preservation"
    )),
    ("lab", _(
        u"sample_preservation_category_vocab_lab",
        default=u"Lab Preservation"
    )),
)

ANALYSIS_TYPES = (
    ("a", _(
        u"analysis_type_analysis",
        default=u"Analysis"
    )),
    ("b", _(
        u"analysis_type_blank",
        default=u"Blank"
    )),
    ("c", _(
        u"analysis_type_control",
        default=u"Control"
    )),
    ("d", _(
        u"analysis_type_duplicate",
        default=u"Duplicate"
    )),
)
