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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims.interfaces import IClient
from bika.lims.utils import chain
from senaite.core.interfaces import IClientAwareMixin
from zope.interface import implementer


@implementer(IClientAwareMixin)
class ClientAwareMixin(object):
    """Method mixin that marks content as client-aware.

    Folderish/non-folderish neutral: combine with
    `senaite.core.content.base.Container` for folderish DX
    content, with `senaite.core.content.base.Item` for
    contentish (non-folderish) DX content, or use as a pure
    interface marker on AT content via the `ClientAwareMixin`
    in `bika.lims.content.clientawaremixin`.
    """
    security = ClassSecurityInfo()

    @security.public
    def getClient(self):
        """Returns the Client the object is bound to, if any
        """
        # Look in the acquisition chain
        for obj in chain(self):
            if IClient.providedBy(obj):
                return obj

        # Look in Schema
        fields = api.get_fields(self)
        client_field = fields.get("Client")
        if client_field:
            client = client_field.get(self)
            client = api.get_object(client, None)
            if client and IClient.providedBy(client):
                return client

        # No client bound
        return None

    @security.public
    def getClientUID(self):
        """Returns the Client UID the object is bound to, if any
        """
        client = self.getClient()
        return client and api.get_uid(client) or ""

    @security.public
    def getClientID(self):
        """Returns the Client ID the object is bound to, if any
        """
        client = self.getClient()
        return client and client.getClientID() or ""

    @security.public
    def getClientTitle(self):
        """Returns the Client Title the object is bound to, if any
        """
        client = self.getClient()
        return client and client.Title() or ""

    @security.public
    def getClientURL(self):
        client = self.getClient()
        return client and client.absolute_url_path() or ""
