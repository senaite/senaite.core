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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFPlone.utils import safe_unicode


def ObjectModifiedEventHandler(batch, event):
    """Actions to be done when a batch is created:
    - Title as the Batch ID if title is not defined
    - Move the Batch inside the Client if defined
    """
    if not batch.title:
        batch.setTitle(safe_unicode(batch.id).encode('utf-8'))

    # If client is assigned, move the Batch the client's folder
    # Note here we directly get the Client from the Schema, cause getClient
    # getter is overriden in Batch content type to always look to aq_parent in
    # order to prevent inconsistencies (the Client schema field is only used to
    # allow the user to assign a Client to the Batch).
    client = batch.getField("Client").get(batch)

    # Check if the Batch is being created inside the Client
    if client and (client.UID() != batch.aq_parent.UID()):
        # move batch inside the client
        cp = batch.aq_parent.manage_cutObjects(batch.id)
        client.manage_pasteObjects(cp)
