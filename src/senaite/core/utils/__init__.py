# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import re

from bika.lims import api
from bika.lims.utils import format_supsub

# Unicode superscript/subscript character mappings
SUPERSCRIPT_MAP = {
    "0": u"\u2070", "1": u"\u00B9", "2": u"\u00B2",
    "3": u"\u00B3", "4": u"\u2074", "5": u"\u2075",
    "6": u"\u2076", "7": u"\u2077", "8": u"\u2078",
    "9": u"\u2079", "+": u"\u207A", "-": u"\u207B",
    "=": u"\u207C", "(": u"\u207D", ")": u"\u207E",
    "n": u"\u207F", "i": u"\u2071",
}

SUBSCRIPT_MAP = {
    "0": u"\u2080", "1": u"\u2081", "2": u"\u2082",
    "3": u"\u2083", "4": u"\u2084", "5": u"\u2085",
    "6": u"\u2086", "7": u"\u2087", "8": u"\u2088",
    "9": u"\u2089", "+": u"\u208A", "-": u"\u208B",
    "=": u"\u208C", "(": u"\u208D", ")": u"\u208E",
}


def _to_unicode_char(char, char_map):
    """Convert a character using the given mapping"""
    return char_map.get(char, char)


def _to_unicode_tag(content, char_map):
    """Convert tag content to Unicode super/subscript"""
    return u"".join(
        _to_unicode_char(c, char_map) for c in content
    )


def format_supsub_unicode(text):
    """Convert super/subscript notation to Unicode characters.

    Handles both raw notation (^, _) and HTML tags (<sup>, <sub>).
    Useful for contexts where HTML cannot be rendered, e.g.
    <option> elements.

    Example: "Bq·kg^-1" -> u"Bq\xb7kg\u207b\xb9"
    Example: "Bq·kg<sup>-1</sup>" -> u"Bq\xb7kg\u207b\xb9"
    """
    if not text:
        return text
    text = api.safe_unicode(text)
    # convert ^ and _ notation to HTML tags first
    if "^" in text or "_" in text:
        text = api.safe_unicode(
            format_supsub(api.to_utf8(text))
        )
    # convert <sup>...</sup> to Unicode superscripts
    text = re.sub(
        r"<sup>(.*?)</sup>",
        lambda m: _to_unicode_tag(
            m.group(1), SUPERSCRIPT_MAP),
        text,
        flags=re.IGNORECASE,
    )
    # convert <sub>...</sub> to Unicode subscripts
    text = re.sub(
        r"<sub>(.*?)</sub>",
        lambda m: _to_unicode_tag(
            m.group(1), SUBSCRIPT_MAP),
        text,
        flags=re.IGNORECASE,
    )
    # strip any remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    return text
