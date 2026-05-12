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

from bika.lims import api
from bika.lims.api.security import get_user_id
from bika.lims.utils import tmpID
from senaite.core.api.dtime import now
from senaite.core.schema.interfaces import IRemarksField
from senaite.core.schema.fields import BaseField
from zope.interface import implementer
from zope.schema import List
from zope.schema.interfaces import IFromUnicode


def fill_remark_object(value):
    user_id = get_user_id()
    properties = api.get_user_properties(user_id)
    fullname = properties and properties.get("fullname") or user_id
    return {
        "id": tmpID(),
        "user_id": user_id,
        "user_name": fullname,
        "created": now(),
        "content": value,
    }


@implementer(IRemarksField, IFromUnicode)
class RemarksField(List, BaseField):
    """A field that handles a remarks for DX content types
    """

    def __init__(self, **kwargs):
        default = kwargs.get("default")
        kwargs["default"] = default or []
        List.__init__(self, **kwargs)
        BaseField.__init__(self, **kwargs)

    def set(self, object, value):
        """Set a remarks record or records
        :param object: the instance of the field
        :param value: dict with remark information or list of dicts
        :type value: list/tuple/dict
        """
        if not isinstance(value, list):
            value = [value]
        super(RemarksField, self).set(object, value)

    def get(self, object):
        """Returns the remarks records
        :param object: the instance of this field
        :returns: list of dicts with remark information for each remark item
        """
        return super(RemarksField, self).get(object) or []

    def add(self, object, value):
        remarks = self.get(object)
        new_remark = fill_remark_object(value)
        remarks.append(new_remark)
        self.set(object, remarks)
