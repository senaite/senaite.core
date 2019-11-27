from AccessControl import ClassSecurityInfo
from Products.Archetypes.BaseObject import BaseObject
from zope.interface import implements

from bika.lims import api
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IClientAwareMixin
from bika.lims.utils import chain


class ClientAwareMixin(BaseObject):
    implements(IClientAwareMixin)

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
        client_field = self.Schema().get("Client", default=None)
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
