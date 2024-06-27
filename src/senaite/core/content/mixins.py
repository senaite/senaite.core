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

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims.interfaces import IClient
from bika.lims.utils import chain
from senaite.core.content.base import Container
from senaite.core.interfaces import IClientAwareMixin
from senaite.core.interfaces import ISampleTypeAwareMixin
from zope.interface import implementer


@implementer(IClientAwareMixin)
class ClientAwareMixin(Container):
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


@implementer(ISampleTypeAwareMixin)
class SampleTypeAwareMixin(Container):
    security = ClassSecurityInfo()

    @security.public
    def getSampleType(self):
        """Returns the sample type(s) assigned to this object, if any
        """
        if ISampleType.providedBy(self):
            return self

        field = self._get_field()
        if not field:
            return None

        sample_type = field.get(self)
        return sample_type or None

    @security.public
    def getSampleTypeUID(self):
        """Returns the UID(s) of the Sample Type(s) assigned to this object
        """
        sample_type = self.getSampleType()
        if isinstance(sample_type, (list, tuple)):
            return map(api.get_uid, sample_type)
        elif sample_type:
            return api.get_uid(sample_type)
        return None

    @security.public
    def getSampleTypeTitle(self):
        """Returns the title or a comma separated list of sample type titles
        """
        sample_type = self.getSampleType()
        if isinstance(sample_type, (list, tuple)):
            title = map(api.get_title, sample_type)
            return ", ".join(title)
        elif sample_type:
            return api.get_title(sample_type)
        return None

    def _get_field(self):
        """Returns the field that stores the SampleType object, if any
        """
        field = self.getField("SampleType", None)
        if not field:
            field = self.getField("SampleTypes", None)

        return field
