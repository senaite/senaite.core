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

import six

from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IMultiUploadField
from zope.interface import implementer
from zope.schema import List
from zope.schema import TextLine


@implementer(IMultiUploadField)
class MultiUploadField(List, BaseField):
    """A field that stores UIDs and upload UUIDs

    This field stores a list of identifiers that can be either:
    - UIDs: for already created file/image objects
    - UUIDs: for uploaded files that need to be converted to objects later
    """

    value_type = TextLine(title=u"UID or UUID")

    def __init__(self, **kw):
        """Initialize the field"""
        # Set default to empty list if not provided
        if "default" not in kw:
            kw["default"] = []
        super(MultiUploadField, self).__init__(**kw)

    def set(self, object, value):
        """Set UIDs and UUIDs

        :param object: The content object
        :param value: List of UIDs/UUIDs or single UID/UUID
        """
        if value is None:
            value = []
        elif isinstance(value, six.string_types):
            value = [value]
        elif not isinstance(value, (list, tuple)):
            value = [value]
        else:
            value = list(value)

        # Filter out empty values
        value = [v for v in value if v]
        super(MultiUploadField, self).set(object, value)

    def get(self, object):
        """Get the stored UIDs/UUIDs

        :param object: The content object
        :returns: List of UIDs/UUIDs
        """
        value = super(MultiUploadField, self).get(object)
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            return [value]
        return list(value)
