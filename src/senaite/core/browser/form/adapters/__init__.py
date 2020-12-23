# -*- coding: utf-8 -*-

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
            "errors": [],
            "messages": [],
            "notifications": [],
            "updates": [],
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
