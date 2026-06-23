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

from zope.interface import Interface
from zope.interface import implements

# Actions carried by a RemarksChangedEvent (the subscriber contract)
ACTION_ADDED = "added"
ACTION_EDITED = "edited"
ACTION_DELETED = "deleted"


class IRemarksAddedEvent(Interface):
    """Remarks Added Event
    """


class RemarksAddedEvent(object):
    implements(IRemarksAddedEvent)

    def __init__(self, context, history):
        self.context = context
        self.history = history


class IRemarksChangedEvent(Interface):
    """Fired when a single remark record is added or edited.

    Carries the affected record, the acting user and the action so that
    subscribers (e.g. a message center) can notify watchers. Note that
    programmatic field writes (imports, migrations) do not emit this event;
    it is fired from the widget endpoints on user-driven changes only.
    """


class RemarksChangedEvent(object):
    implements(IRemarksChangedEvent)

    def __init__(self, context, record, actor, action):
        self.context = context
        self.record = record
        self.actor = actor
        self.action = action
