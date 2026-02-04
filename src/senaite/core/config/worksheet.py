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

from bika.lims import senaiteMessageFactory as _


WORKSHEET_LAYOUT_OPTIONS = (
    ("analyses_classic_view", _(
        u"analyses_classic_view_name",
        default=u"Classic"
    )),
    ("analyses_transposed_view", _(
        u"analyses_transposed_view_name",
        default=u"Transposed"
    )),
)

DEFAULT_WORKSHEET_LAYOUT = "analyses_classic_view"

# Add-on folder to look for templates
WS_TEMPLATES_ADDON_DIR = "worksheets"
