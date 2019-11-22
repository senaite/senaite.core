from AccessControl import ClassSecurityInfo
from Products.Archetypes.BaseObject import BaseObject
from zope.interface import implements

from bika.lims import api
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IClientBindable


class ClientBindable(BaseObject):
    implements(IClientBindable)

    security = ClassSecurityInfo()

    @security.public
    def getClient(self):
        """Returns the Client the object is bound to, if any
        """
        # Look for the parent
        client = self._infere_client()
        if client:
            return client

        # Look in Schema
        client_field = self.Schema().get("Client", default=None)
        if client_field:
            client = client_field.get(self)
            client = api.get_object(client, None)
            if client and IClient.providedBy(client):
                return client

        # No client bound
        return None

    def _infere_client(self, obj=None):
        """Inferes the client the object belongs to by walking through parents
        """
        if not obj:
            obj = self
        if IClient.providedBy(obj):
            return obj
        elif api.is_portal(obj):
            return None
        return self._infere_client(obj.aq_parent)

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
