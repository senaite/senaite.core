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

from senaite.core.api.remarks import apply_delete
from senaite.core.api.remarks import apply_edit
from senaite.core.api.remarks import apply_restore
from senaite.core.api.remarks import find_record
from senaite.core.api.remarks import make_record
from senaite.core.schema.interfaces import IRemarksField
from senaite.core.schema.fields import BaseField
from zope.interface import implementer
from zope.schema import List
from zope.schema.interfaces import IFromUnicode


def fill_remark_object(value):
    """Create a new remark record for the given content
    """
    return make_record(value)


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
        """Append a new remark record for the given content
        :param object: the instance of this field
        :param value: the content of the new remark
        :returns: the new remark record
        """
        remarks = self.get(object)
        new_remark = make_record(value)
        remarks.append(new_remark)
        self.set(object, remarks)
        return new_remark

    def edit(self, object, remark_id, value):
        """Edit the content of an existing remark record, keeping the prior
        content as a version.
        :param object: the instance of this field
        :param remark_id: the id of the remark record to edit
        :param value: the new content of the remark
        :returns: the updated remark record or None if not found
        """
        remarks = self.get(object)
        index, record = find_record(remarks, remark_id)
        if record is None:
            return None
        apply_edit(record, value)
        remarks[index] = record
        self.set(object, remarks)
        return record

    def delete(self, object, remark_id):
        """Soft-delete an existing remark record, keeping it for audit but
        marking it as deleted.
        :param object: the instance of this field
        :param remark_id: the id of the remark record to delete
        :returns: the deleted remark record or None if not found
        """
        remarks = self.get(object)
        index, record = find_record(remarks, remark_id)
        if record is None:
            return None
        apply_delete(record)
        remarks[index] = record
        self.set(object, remarks)
        return record

    def restore(self, object, remark_id):
        """Restore a soft-deleted remark record, making it visible again.
        :param object: the instance of this field
        :param remark_id: the id of the remark record to restore
        :returns: the restored remark record or None if not found
        """
        remarks = self.get(object)
        index, record = find_record(remarks, remark_id)
        if record is None:
            return None
        apply_restore(record)
        remarks[index] = record
        self.set(object, remarks)
        return record
