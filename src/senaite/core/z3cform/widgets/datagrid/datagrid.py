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

from collective.z3cform.datagridfield.datagridfield import DataGridField
from collective.z3cform.datagridfield.datagridfield import DataGridFieldObject
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IDataGridField
from senaite.core.schema.interfaces import IDataGridRow
from senaite.core.z3cform.interfaces import IDataGridRowWidget
from senaite.core.z3cform.interfaces import IDataGridWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.schema.interfaces import IObject


@implementer(IDataGridWidget)
class DataGridWidget(DataGridField):
    """Senaite DataGrid Widget
    """
    display_table_css_class = "datagridwidget-table-view"

    def createObjectWidget(self, idx):
        """Create row widget
        """
        valueType = self.field.value_type

        if IObject.providedBy(valueType):
            widget = DataGridRowWidgetFactory(valueType, self.request)
            widget.setErrors = idx not in ["TT", "AA"]
        else:
            widget = getMultiAdapter((valueType, self.request), IFieldWidget)

        return widget


@adapter(IDataGridField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def DataGridWidgetFactory(field, request):
    """Widget factory for DataGrid
    """
    return FieldWidget(field, DataGridWidget(request))


@implementer(IDataGridRowWidget)
class DataGridRowWidget(DataGridFieldObject):
    """Senaite DataGridRow Widget
    """


@adapter(IDataGridRow, ISenaiteFormLayer)
@implementer(IFieldWidget)
def DataGridRowWidgetFactory(field, request):
    """Widget factory for DataGridRow
    """
    return FieldWidget(field, DataGridRowWidget(request))
