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

from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent


class IUIDReferenceCreatedEvent(IObjectEvent):
    """An event fired after a reference between two objects was cretated
    """


class IUIDReferenceDestroyedEvent(IObjectEvent):
    """An event fired after a reference between two objects was destroyed
    """


@implementer(IUIDReferenceCreatedEvent)
class UIDReferenceCreated(object):

    def __init__(self, field, source, target):
        """Reference Created Event

        :param field: The field on the source object
        :param source: The context object holding the UID reference field
        :param target: The context object being referenced
        """
        self.field = field
        self.source = source
        self.target = target

        # See IObjectEvent
        # -> Allow to define an event subscriber for a custom type
        self.object = source


@implementer(IUIDReferenceDestroyedEvent)
class UIDReferenceDestroyed(object):

    def __init__(self, field, source, target):
        """Reference Destroyed Event

        :param field: The field on the source object
        :param source: The context object holding the UID reference field
        :param target: The context object being referenced
        """
        self.field = field
        self.source = source
        self.target = target

        # See IObjectEvent
        # -> Allow to define an event subscriber for a custom type
        self.object = source
