# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims.interfaces import IDeactivable
from plone.dexterity.content import Container
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.interfaces import IClientsGroup
from senaite.core.schema.uidreferencefield import get_backrefs
from zope import schema
from zope.interface import implementer


class IClientsGroupSchema(model.Schema):
    """Schema interface for ClientGroup content
    """

    title = schema.TextLine(
        title=u"Title",
        required=True,
    )

    description = schema.TextLine(
        title=u"Description",
        required=False,
    )


@implementer(IClientsGroup, IClientsGroupSchema, IDeactivable)
class ClientsGroup(Container):
    """ClientsGroup content
    """

    # Catalogs where this type will be catalogued
    _catalogs = ["portal_catalog"]

    security = ClassSecurityInfo()
    exclude_from_nav = True

    @security.protected(permissions.View)
    def getRawClients(self):
        """Returns the UIDs of the clients assigned to this group
        """
        return get_backrefs(self, relationship="ClientGroupClients")

    @security.protected(permissions.View)
    def getClients(self):
        """Returns the UIDs of the clients assigned to this group
        """
        return [api.get_object(uid) for uid in self.getRawClients()]
