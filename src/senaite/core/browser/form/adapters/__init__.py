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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from senaite.core.interfaces import IAjaxEditForm
from zope.interface import implementer


@implementer(IAjaxEditForm)
class EditFormAdapterBase(object):
    """Base class for EditForm Adapters
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._data = {
            "hide": [],
            "show": [],
            "readonly": [],
            "editable": [],
            "errors": [],
            "messages": [],
            "notifications": [],
            "updates": [],
            "html": [],
            "attributes": [],
        }

    @property
    def data(self):
        return self._data

    def initialized(self, data):
        return NotImplementedError("Must be implemented by subclass")

    def modified(self, data):
        return NotImplementedError("Must be implemented by subclass")

    def add_record_to(self, key, record):
        """Add a record to the dictionary
        """
        # always operate on a copy of the item
        value = self._data.get(key, [])[:]
        # append the record to the list
        value.append(record)
        # set the value back on the dictionary
        self._data[key] = value

    def add_hide_field(self, name, **kw):
        """Add the field to the `hide` list
        """
        record = dict(name=name, **kw)
        self.add_record_to("hide", record)

    def add_show_field(self, name, **kw):
        """Add the field to the show list
        """
        record = dict(name=name, **kw)
        self.add_record_to("show", record)

    def add_readonly_field(self, name, message=None, **kw):
        """Add field to the readonly list
        """
        record = dict(name=name, message=message, **kw)
        self.add_record_to("readonly", record)

    def add_editable_field(self, name, message=None, **kw):
        """Add field to the editable list
        """
        record = dict(name=name, message=message, **kw)
        self.add_record_to("editable", record)

    def add_error_field(self, name, error, **kw):
        """Add field to the error list
        """
        record = dict(name=name, error=error, **kw)
        self.add_record_to("errors", record)

    def add_status_message(self, message, level="info", **kw):
        """Add status message to the messages list
        """
        record = dict(message=message, level=level, **kw)
        self.add_record_to("messages", record)

    def add_notification(self, title, message, **kw):
        """Add status message to the messages list
        """
        record = dict(title=title, message=message, **kw)
        self.add_record_to("notifications", record)

    def add_update_field(self, name, value, **kw):
        """Add field to the update list
        """
        record = dict(name=name, value=value, **kw)
        self.add_record_to("updates", record)

    def add_inner_html(self, selector, html, **kw):
        """Add inner html to an element
        """
        record = dict(selector=selector, html=html, **kw)
        self.add_record_to("html", record)

    def add_attribute(self, selector, name, value, **kw):
        """Add an attribute to an element
        """
        record = dict(selector=selector, name=name, value=value, **kw)
        self.add_record_to("attributes", record)
