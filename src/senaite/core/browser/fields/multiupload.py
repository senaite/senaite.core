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

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Registry import registerField


class MultiUploadField(ObjectField):
    """A field that stores UIDs and upload UUIDs

    This field stores a list of identifiers that can be either:
    - UIDs: for already created file/image objects
    - UUIDs: for uploaded files that need to be converted to objects later
    """
    _properties = ObjectField._properties.copy()
    _properties.update({
        "type": "multiupload",
        "default": [],
        })

    security = ClassSecurityInfo()

    @security.private
    def set(self, instance, value, **kwargs):
        """Store UIDs and UUIDs as a list

        :param instance: The content object
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
        super(MultiUploadField, self).set(instance, value, **kwargs)

    @security.public
    def get(self, instance, **kwargs):
        """Get the stored UIDs/UUIDs

        :param instance: The content object
        :returns: List of UIDs/UUIDs
        """
        value = super(MultiUploadField, self).get(instance, **kwargs)
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            return [value]
        return list(value)

    @security.public
    def getRaw(self, instance, **kwargs):
        """Get the raw stored value

        :param instance: The content object
        :returns: List of UIDs/UUIDs
        """
        return self.get(instance, **kwargs)


InitializeClass(MultiUploadField)

registerField(
    MultiUploadField,
    title="Multi Upload",
    description="Stores UIDs and upload UUIDs for deferred file creation")
