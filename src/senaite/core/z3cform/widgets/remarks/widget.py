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

from senaite.core.schema.interfaces import IRemarksField
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.z3cform.interfaces import IRemarksWidget
from z3c.form.browser.widget import HTMLFormElement
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer


@implementer(IRemarksWidget)
class RemarksWidget(HTMLFormElement, Widget):
    """SENAITE Remarks Widget
    """
    klass = u"senaite-remarks-widget"


@adapter(IRemarksField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def RemarksWidgetFactory(field, request):
    """Widget factory for Address Widget
    """
    return FieldWidget(field, RemarksWidget(request))
