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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
import six

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.interfaces import IRemarksField
from DateTime import DateTime
from Products.Archetypes.event import ObjectEditedEvent
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Registry import registerField
from zope import event
from zope.interface import implements
from bika.lims import api
from bika.lims.utils import tmpID


class RemarksHistory(list):
    """A list containing a remarks history, but __str__ returns the legacy
    format from instances prior v1.3.3
    """
    def to_legacy(self):
        """Returns the remarks in legacy format
        """
        remarks = list()
        for record in self:
            msg = record.get("content")
            if not msg:
                continue
            date_msg = record.get("date")
            user_name = record.get("user_name")
            if date_msg and user_name:
                # Build the legacy format
                msg = "=== {} ({})\n{}".format(date_msg, user_name, msg)
            remarks.append(msg)
        return "\n".join(remarks)

    def __str__(self):
        """Returns the remarks in legacy format
        """
        return self.to_legacy()

    def __eq__(self, y):
        if isinstance(y, six.string_types):
            return str(self) == y
        return super(list, self).__eq__(y)


class RemarksField(ObjectField):
    """A field that stores remarks.  The value submitted to the setter
    will always be appended to the actual value of the field.
    A divider will be included with extra information about the text.
    """

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'remarks',
        'widget': RemarksWidget,
        'default': '',
    })

    implements(IRemarksField)

    security = ClassSecurityInfo()

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """Adds the value to the existing text stored in the field,
        along with a small divider showing username and date of this entry.
        """
        if not value:
            return

        if isinstance(value, RemarksHistory):
            # Override the whole history here
            history = value
        else:
            # Create a new history record
            record = self.to_history_record(value)

            # Append the new record to the history
            history = self.get_history(instance)
            history.append(record)

        # Generate the json and store
        remarks = json.dumps(history)
        ObjectField.set(self, instance, remarks)

        # notify object edited event
        event.notify(ObjectEditedEvent(instance))

    def to_history_record(self, value):
        """Transforms the value to an history record
        """
        value = value.strip()
        user = getSecurityManager().getUser()
        contact = api.get_user_contact(user)
        record = {
            "id": tmpID(),
            "date": DateTime().ISO(),
            "user_name": user.getUserName(),
            "user_full_name": contact and contact.getFullname() or "",
            "content": value,
        }
        return record

    def get_history(self, instance):
        """Returns a RemarksHistory object with the remarks entries
        """
        remarks = instance.getRawRemarks()
        if not remarks:
            return []
        try:
            records = json.loads(remarks)
        except ValueError as ex:
            # This is for backwards compatibility with legacy format < v1.3.3
            records = [{"id": tmpID(),
                        "date": "",
                        "user_name": "",
                        "user_full_name": "",
                        "content": remarks}]
        return RemarksHistory(records)

    def to_html(self, value):
        """Convert the value to HTML format
        """
        return api.text_to_html(value)

    def get(self, instance, **kwargs):
        """Returns the value in legacy format
        """
        return str(self.get_history(instance))

    def getRaw(self, instance, **kwargs):
        """Returns raw field value (possible wrapped in BaseUnit)
        """
        value = ObjectField.get(self, instance, **kwargs)
        # getattr(instance, "Remarks") returns a BaseUnit
        if callable(value):
            value = value()
        return value


registerField(RemarksField, title='Remarks', description='')
