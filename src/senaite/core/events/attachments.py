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

from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent


class IAttachmentsDeletedEvent(IObjectEvent):
    """An event fired after attachments were deleted from an object
    """


@implementer(IAttachmentsDeletedEvent)
class AttachmentsDeletedEvent(object):

    def __init__(self, container, deleted):
        """Attachment Deleted Event

        :param container: Conbtainer that held the attachments
        :param deleted: List of deleted attachments
        """
        self.container = container
        self.deleted = deleted

        # See IObjectEvent
        # -> Allow to define an event subscriber for a custom type
        self.object = container
