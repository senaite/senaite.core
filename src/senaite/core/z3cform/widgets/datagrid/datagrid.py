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

from bika.lims import api
from collective.z3cform.datagridfield.datagridfield import DataGridField
from collective.z3cform.datagridfield.datagridfield import DataGridFieldObject
from plone.formwidget.namedfile.converter import b64decode_file
from plone.formwidget.namedfile.converter import b64encode_file
from plone.formwidget.namedfile.widget import Download as DownloadBase
from plone.formwidget.namedfile.widget import NamedFileWidget
from plone.namedfile import NamedBlobFile
from plone.namedfile.utils import stream_data
from Products.Five.browser import BrowserView
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IDataGridField
from senaite.core.schema.interfaces import IDataGridRow
from senaite.core.z3cform.interfaces import IDataGridRowWidget
from senaite.core.z3cform.interfaces import IDataGridWidget
from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import NO_VALUE
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.schema.interfaces import IObject


@implementer(IDataGridWidget)
class DataGridWidget(DataGridField):
    """Senaite DataGrid Widget
    """
    display_table_css_class = "datagridwidget-table-view"
    templates = {}

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

    def render(self):
        if self.mode in self.templates.keys():
            return ViewPageTemplateFile(self.templates[self.mode])(self)
        return super(DataGridWidget, self).render()


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


class DataGridRowFileWidget(NamedFileWidget):
    """File Widget that can be used in DGF Rows
    """
    def render(self):
        """Use a custom input mode template for row based file fields
        """
        if self.mode == INPUT_MODE:
            # render a custom input template
            return ViewPageTemplateFile("datagridrow_file_input.pt")(self)
        elif self.mode == DISPLAY_MODE:
            # render a custom display template
            return ViewPageTemplateFile("datagridrow_file_display.pt")(self)
        return super(DataGridRowFileWidget, self).render()

    @property
    def filedata(self):
        """Return the base64 encoded filedata
        """
        if not self.value:
            return ""
        filename = self.value.filename
        filedata = self.value.data
        return b64encode_file(filename, filedata)

    def extract(self, default=NO_VALUE):
        """Extract the base64 encoded file from the file input field

        NOTE:
        The file widget allows to "keep" files by handling a "nochange" action.
        However, this requires that the original file can be looked up by this
        widget class and this is not possible, even if we would have access to
        the context itself. E.g. we do not know which file is located in which
        record of the original field, especially after the rows have been
        reordered etc..
        Therefore, we serialize the original file in a hidden field and ensure
        that we can reconstruct it from there.
        """
        filedata = self.request.form.get(self.name + "-filedata")
        if filedata:
            filename, data = b64decode_file(filedata)
            namedfile = NamedBlobFile(data=data, filename=filename)
            return namedfile
        value = super(DataGridRowFileWidget, self).extract(default=default)
        if isinstance(value, list):
            # NOTE: allow_insert=True of the DGF widget adds copies of the TT
            #       (template) row, which gives us here multiple files and we
            #       get an error on submit.
            #       -> configure the datagrid widget with allow_insert=False!
            return default
        return value


@implementer(IPublishTraverse)
class Download(DownloadBase):
    """Download a file located in a datagrid row

    Example:
    ../context/++field++my-datagrid-records-field/@@download/0/fieldname
    """

    def __init__(self, field, request):
        self.field = field
        self.context = field.context
        # required for security checking
        super(BrowserView, self).__init__(self.context, request)
        self.index = None
        self.fieldname = None
        # required by self.set_headers
        self.filename = None

    def publishTraverse(self, request, name):
        if self.index is None:  # ../@@download/index
            self.index = api.to_int(name, 0)
        elif self.fieldname is None:  # ../@@download/index/fieldname
            self.fieldname = name
        else:
            raise NotFound(self, name, request)
        return self

    def __call__(self):
        # get the records
        records = self.field.get(self.context)
        # try to get the record at the given index
        try:
            record = records[self.index]
        except IndexError:
            raise NotFound(self, self.index, self.request)
        # try to get the file
        file = record.get(self.fieldname)
        if not file:
            raise NotFound(self, self.fieldname, self.request)
        self.set_headers(file)
        request_range = self.handle_request_range(file)
        return stream_data(file, **request_range)


@adapter(IDataGridRow, ISenaiteFormLayer)
@implementer(IFieldWidget)
def DataGridRowWidgetFactory(field, request):
    """Widget factory for DataGridRow
    """
    return FieldWidget(field, DataGridRowWidget(request))
