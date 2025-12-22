# -*- coding: utf-8 -*-

import six

from Products.CMFPlone.utils import safe_unicode
from senaite.core.schema.fields import BaseField
from zope import schema


class TextLineField(schema.TextLine, BaseField):
    """A text field with no newlines and without leading and trailing spaces.
    """

    def set(self, object, value):
        """Set the field's value to the given object.
        The value is converted to a Unicode string to preserve compatibility
        with the legacy behavior of auto-generated setters in AT content types.
        Leading and trailing whitespaces are removed before assignment.
        """
        value = safe_unicode(value)
        if isinstance(value, six.string_types):
            value = value.strip()
        super(TextLineField, self).set(object, value)

    def get(self, object):
        """Sets the value of this field from the given object.
        The returned value is encoded as UTF-8 to maintain compatibility with
        the legacy behavior of auto-generated getters in AT content types.
        """
        value = super(TextLineField, self).get(object)
        if isinstance(value, six.string_types):
            value = value.encode("utf-8")
        return value
