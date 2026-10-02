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

import zope.interface
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IColorField
from senaite.core.z3cform.interfaces import IColorWidget
from z3c.form import interfaces
from z3c.form.browser import text
from z3c.form.browser import widget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer_only


@implementer_only(IColorWidget)
class ColorWidget(text.TextWidget):
    """Renders an HTML5 `<input type="color">` picker.
    """
    klass = u"senaite-color-widget"
    value = u""

    def update(self):
        super(ColorWidget, self).update()
        widget.addFieldClass(self)
        # NOTE: deliberately do NOT add `form-control` here — it
        # forces `width: 100%` and stretches the color picker
        # across the full row. The square footprint comes from the
        # input template.


@adapter(IColorField, ISenaiteFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ColorWidgetFactory(field, request):
    """IFieldWidget widget factory for ColorWidget.
    """
    return FieldWidget(field, ColorWidget(request))
