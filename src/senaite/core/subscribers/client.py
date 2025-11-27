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
from senaite.core.registry import get_registry_record


def on_client_created(client, event):
    """Event handler when a new Client was created
    """
    if get_registry_record("auto_create_client_group", True):
        # create a new client group
        client.create_group()


def on_attachments_deleted(container, event):
    """Event handler when attachments were deleted
    """
    deleted = event.deleted

    # Remove stale references from the attachments field
    deleted_attachments = [api.get_uid(obj) for obj in deleted]
    current_attachments = container.getRawAttachments() or []

    new_attachments = [uid for uid in current_attachments
                       if uid not in deleted_attachments]

    container.setAttachments(new_attachments)
