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

import copy
import six

from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from bika.lims import api
from bika.lims.decorators import returns_json
from senaite.core.api.dtime import to_localized_time
from senaite.core.schema.interfaces import IRemarksField
from senaite.core.schema.remarksfield import fill_remark_object
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.p3compat import cmp
from senaite.core.permissions import FieldEditRemarks
from senaite.core.z3cform.interfaces import IRemarksWidget
from z3c.form.browser import widget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.interface import implementer


def check_permission_edit_remark(context):
    """Check is can add remark
    """
    tool = api.get_tool("portal_membership")
    return tool.checkPermission(FieldEditRemarks, context)


@adapter(IRemarksField, IWidget)
class RemarksDataConverter(BaseDataConverter):
    """Value conversion between field and widget
    """
    def to_list_of_dicts(self, value):
        if not isinstance(value, list):
            value = [value]
        value = filter(None, value)
        return map(self.to_dict, value)

    def to_dict(self, value):
        if not isinstance(value, dict):
            return {}
        return value

    def toWidgetValue(self, value):
        """Returns the field value with encoded string
        """
        values = self.to_list_of_dicts(value)
        values = self.to_utf8(values)
        values.sort(lambda x, y: cmp(y["created"], x["created"]))
        return values

    def toFieldValue(self, value):
        """Converts from widget value to safe_unicode
        """
        if api.is_string(value):
            value = fill_remark_object(value)
        values = self.to_list_of_dicts(value)
        return self.to_safe_unicode(values)

    def to_safe_unicode(self, data):
        """Converts the data to unicode
        """
        if isinstance(data, unicode):
            return data
        if isinstance(data, list):
            return [self.to_safe_unicode(item) for item in data]
        if isinstance(data, dict):
            return {
                self.to_safe_unicode(key): self.to_safe_unicode(value)
                for key, value in six.iteritems(data)
            }
        return safe_unicode(data)

    def to_utf8(self, data):
        """Encodes the data to utf-8
        """
        if isinstance(data, unicode):
            return data.encode("utf-8")
        if isinstance(data, list):
            return [self.to_utf8(item) for item in data]
        if isinstance(data, dict):
            return {
                self.to_utf8(key): self.to_utf8(value)
                for key, value in six.iteritems(data)
            }
        return data


@implementer(IRemarksWidget)
class RemarksWidget(widget.HTMLFormElement, Widget):
    """SENAITE Remarks Widget
    """
    klass = u"senaite-remarks-widget"

    def update(self):
        widget.HTMLFormElement.update(self)
        Widget.update(self)
        widget.addFieldClass(self)

    def render(self):
        if self.is_add_form():
            return ViewPageTemplateFile("add.pt")(self)
        return Widget.render(self)

    def is_add_form(self):
        """Check if we are in an add form
        :returns: True if in add form, False if in edit form
        """
        # Check if the parent form implements IAddForm
        form = getattr(self, "form", None)
        if form is None:
            return False
        is_add = IAddForm.providedBy(form)

        # form maybe includes into group(fieldset)
        # check that recursively
        parent = aq_parent(aq_inner(form))
        while not is_add and parent is not None:
            is_add = IAddForm.providedBy(parent)
            parent = aq_parent(aq_inner(parent))
        return is_add

    def localized_time(self, value):
        return to_localized_time(value,
                                 long_format=True,
                                 context=self.context,
                                 request=self.request)

    def html_content(self, value):
        return api.text_to_html(value)

    @property
    def portal(self):
        """Return the portal object
        """
        return api.get_portal()

    @property
    def portal_url(self):
        """Return the portal object URL
        """
        return api.get_url(self.portal)

    @property
    def can_add_remark(self):
        """Check is can add remark
        """
        modes = [INPUT_MODE, DISPLAY_MODE]
        can_edit_field = check_permission_edit_remark(self.context)
        return self.mode in modes and can_edit_field


@adapter(IRemarksField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def RemarksWidgetFactory(field, request):
    """Widget factory for Address Widget
    """
    return FieldWidget(field, RemarksWidget(request))


class AjaxAddRemark(BrowserView):
    """Endpoint for the add remark for object
    """

    @returns_json
    def __call__(self):
        """Returns a json with the result about of added remark for object
        """
        field_name = self.request.form.get("fieldName", None)
        uid = self.request.form.get("uid", None)
        value = self.request.form.get("value", None)
        if not field_name or not uid or not value:
            return {"success": False}
        obj = api.get_object_by_uid(uid, None)
        if not obj:
            return {"success": False}
        new_remark = self.add_remark_to_obj(obj, field_name, value)
        if not new_remark:
            return {"success": False}
        return {"success": True}

    def add_remark_to_obj(self, obj, field_name, value):
        """Add new remark to `obj` by `field_name` with `value`
        """
        fields = api.get_fields(obj)
        if field_name not in fields:
            return False
        field = fields.get(field_name)
        if not IRemarksField.providedBy(field):
            return False
        if not check_permission_edit_remark(obj):
            self.request.response.setStatus(403)
            return False
        field.add(obj, value)
        return True


class AjaxFetchRemarks(BrowserView):
    """Endpoint for fetching remarks for object
    """
    @returns_json
    def __call__(self):
        uid = self.request.form.get("uid", None)
        field_name = self.request.form.get("fieldName", None)
        if not uid or not field_name:
            return {"success": False}
        obj = api.get_object_by_uid(uid, None)
        if not obj:
            return {"success": False}

        value = self.get_remarks_by_field(obj, field_name)
        if not value:
            return {"success": False}
        remarks = copy.deepcopy(value)
        remarks.sort(lambda x, y: cmp(y["created"], x["created"]))
        for r in remarks:
            r["created"] = to_localized_time(r["created"],
                                             long_format=True,
                                             context=self.context,
                                             request=self.request)
        return {
            "success": True,
            "remarks": remarks,
        }

    def get_remarks_by_field(self, obj, field_name):
        fields = api.get_fields(obj)
        if field_name not in fields:
            return False
        field = fields.get(field_name)
        if not IRemarksField.providedBy(field):
            return False
        return field.get(obj)
