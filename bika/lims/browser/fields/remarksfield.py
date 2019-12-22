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
from DateTime import DateTime
from Products.Archetypes.Field import ObjectField
from Products.Archetypes.Registry import registerField
from Products.Archetypes.event import ObjectEditedEvent
from zope import event
from zope.interface import implements

from bika.lims import api
from bika.lims.browser.widgets import RemarksWidget
from bika.lims.interfaces import IRemarksField
from bika.lims.utils import tmpID
from datetime import datetime

from Products.ATContentTypes.utils import DT2dt
from dateutil.relativedelta import relativedelta
from bika.lims.browser import ulocalized_time
import pytz


class RemarksHistory(list):
    """A list containing a remarks history, but __str__ returns the legacy
    format from instances prior v1.3.3
    """

    def html(self):
        return api.text_to_html(str(self))

    def __str__(self):
        """Returns the remarks in legacy format
        """
        remarks = map(lambda rec: str(rec), self)
        remarks = filter(None, remarks)
        return "\n".join(remarks)

    def __eq__(self, y):
        if isinstance(y, six.string_types):
            return str(self) == y
        return super(list, self).__eq__(y)


class RemarksHistoryRecord(dict):
    """A dict implementation that represents a record/entry of Remarks History
    """

    def __init__(self, *arg, **kw):
        super(RemarksHistoryRecord, self).__init__(*arg, **kw)
        self["id"] = self.id or tmpID()
        self["user_id"] = self.user_id
        self["user_name"] = self.user_name
        self["created"] = self.created or DateTime().ISO()
        self["content"] = self.content

    @property
    def id(self):
        return self.get("id", "")

    @property
    def user_id(self):
        return self.get("user_id", "")

    @property
    def user_name(self):
        return self.get("user_name", "")

    @property
    def created(self):
        return self.get("created", "")

    @property
    def content(self):
        return self.get("content", "")

    @property
    def html_content(self):
        return api.text_to_html(self.content)

    @property
    def friendly_created(self):
        """Formats to `h m s` if the elapsed time between now and the time
        passed-in is less than 1 month. Otherwise, returns the date time in
        long format
        """
        if not self.created:
            return ""

        date_from = DT2dt(api.to_date(self.created)).replace(tzinfo=pytz.utc)
        date_to = datetime.now().replace(tzinfo=pytz.utc)
        diff = relativedelta(date_to, date_from)
        if diff.years or diff.months:
            return ulocalized_time(self.created, long_format=True,
                                   context=api.get_portal())
        if diff.days > 5:
            return ulocalized_time(self.created, long_format=True,
                                   context=api.get_portal())
        if diff.days:
            tuples = [(diff.days, "d"), (diff.hours, "h")]
        elif diff.hours:
            tuples = [(diff.hours, "h"), (diff.minutes, "m")]
        else:
            tuples = [(diff.minutes, "m"), (diff.seconds, "s")]

        # Boil out empties
        tuples = filter(lambda tup: tup[0] > 0, tuples)
        tokens = map(lambda tup: "{}{}".format(tup[0], tup[1]), tuples)
        return " ".join(tokens)

    def __str__(self):
        """Returns a legacy string format of the Remarks record
        """
        if not self.content:
            return ""
        if self.created and self.user_id:
            # Build the legacy format
            return "=== {} ({})\n{}".format(self.created, self.user_id,
                                            self.content)
        return self.content


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

    @property
    def searchable(self):
        """Returns False, preventing this field to be searchable by AT's
        SearcheableText
        """
        return False

    def set(self, instance, value, **kwargs):
        """Adds the value to the existing text stored in the field,
        along with a small divider showing username and date of this entry.
        """
        if not value:
            return

        if isinstance(value, RemarksHistory):
            # Override the whole history here
            history = value

        elif isinstance(value, (list, tuple)):
            # This is a list, convert to RemarksHistory
            history = RemarksHistory(list(value))

        elif isinstance(value, RemarksHistoryRecord):
            # This is a record, append to the history
            history = self.get_history(instance)
            history.append(value)

        elif isinstance(value, six.string_types):
            # Create a new history record
            record = self.to_history_record(value)

            # Append the new record to the history
            history = self.get_history(instance)
            history.append(record)

        else:
            raise ValueError("Type not supported: {}".format(type(value)))

        # Store the data
        ObjectField.set(self, instance, history)

        # notify object edited event
        event.notify(ObjectEditedEvent(instance))

    def to_history_record(self, value):
        """Transforms the value to an history record
        """
        user = api.get_current_user()
        contact = api.get_user_contact(user)
        full_name = contact and contact.getFullname() or ""
        return RemarksHistoryRecord(user_id=user.id,
                                    user_name=full_name,
                                    content=value.strip())

    def get_history(self, instance):
        """Returns a RemarksHistory object with the remarks entries
        """
        remarks = instance.getRawRemarks()
        if not remarks:
            return RemarksHistory()

        # Backwards compatibility with legacy from < v1.3.3
        if isinstance(remarks, six.string_types):
            remark = RemarksHistoryRecord(content=remarks.strip())
            remarks = RemarksHistory([remark,])

        return remarks

    def get(self, instance, **kwargs):
        """Returns a RemarksHistory object
        """
        return self.get_history(instance)

    def getRaw(self, instance, **kwargs):
        """Returns raw field value (possible wrapped in BaseUnit)
        """
        value = ObjectField.get(self, instance, **kwargs)
        # getattr(instance, "Remarks") returns a BaseUnit
        if callable(value):
            value = value()
        return value


registerField(RemarksField, title='Remarks', description='')
