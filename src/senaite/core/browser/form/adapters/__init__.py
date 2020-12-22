# -*- coding: utf-8 -*-

from six import string_types

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
            "update": {},
            "errors": {},
            "messages": [],
        }

    @property
    def data(self):
        return self._data

    def hide_field(self, name):
        """Add the field to the `hide` list
        """
        if not isinstance(name, string_types):
            raise TypeError("Value must be a string type, got '{}'"
                            .format(type(name)))
        key = "hide"
        value = self._data.get(key, [])[:]
        if name not in value:
            value.append(name)
        self._data[key] = value

    def show_field(self, name):
        """Add the field to the show list
        """
        if not isinstance(name, string_types):
            raise TypeError("Name must be a string type, got '{}'"
                            .format(type(name)))
        key = "show"
        value = self._data.get(key, [])[:]
        if name not in value:
            value.append(name)
        self._data[key] = value

    def set_field_error(self, name, error):
        """Set field error
        """
        key = "errors"
        value = self._data.get(key, {})
        value[name] = error
        self._data[key] = value

    def set_status_message(self, message, level="info"):
        """Set status message
        """
        if message is None:
            return
        key = "messages"
        value = self._data.get(key, [])[:]
        value.append({"level": level, "message": message})
        self._data[key] = value

    def initialized(self, data):
        return NotImplementedError("Must be implemented by subclass")

    def modified(self, data):
        return NotImplementedError("Must be implemented by subclass")
