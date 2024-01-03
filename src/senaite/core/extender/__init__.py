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

from archetypes.schemaextender.field import ExtensionField
from bika.lims import api
from Products.Archetypes.Field import LinesField
from senaite.core.api import label as label_api


class ExtLabelField(ExtensionField, LinesField):
    """Extended Field for Labels
    """
    def get(self, instance, **kw):
        labels = label_api.get_obj_labels(instance)
        return labels

    def set(self, instance, value, **kw):
        if api.is_string(value):
            value = filter(None, value.split("\r\n"))
        labels = label_api.to_labels(value)
        return label_api.set_obj_labels(instance, labels)
