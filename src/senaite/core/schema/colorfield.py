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

from senaite.core.schema.interfaces import IColorField
from senaite.core.schema.textlinefield import TextLineField
from zope.interface import implementer
from zope.schema import ValidationError


HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class InvalidColorValue(ValidationError):
    __doc__ = u"Color value must be a 6-digit hex string (#rrggbb)."


@implementer(IColorField)
class ColorField(TextLineField):
    """A field storing a 6-digit hex color string `#rrggbb`.

    Renders as the native HTML5 `<input type="color">` picker in the
    edit form. An empty value is allowed when `required=False`.
    """

    def _validate(self, value):
        super(ColorField, self)._validate(value)
        if not value:
            return
        if not HEX_COLOR_RE.match(value):
            raise InvalidColorValue(value)
