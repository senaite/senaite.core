# -*- coding: utf-8 -*-

from plone.dexterity.content import Container
from plone.supermodel import model
from senaite.core.interfaces import IClientsGroups
from zope.interface import implementer


class IClientsGroupsSchema(model.Schema):
    """Schema interface for ClientGroups content
    """


@implementer(IClientsGroups, IClientsGroupsSchema)
class ClientsGroups(Container):
    """Folder for ClientsGroup content
    """
