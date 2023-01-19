# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from bika.lims import api
from plone.dexterity.content import Container as BaseContainer
from plone.dexterity.content import Item as BaseItem
from senaite.core.interfaces import IContainer
from senaite.core.interfaces import IItem
from zope.interface import implementer


@implementer(IContainer)
class Container(BaseContainer):
    """Base class for SENAITE folderish contents
    """
    security = ClassSecurityInfo()

    @security.private
    def accessor(self, fieldname, raw=False):
        """Return the field accessor for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        field = schema[fieldname]
        if raw:
            if hasattr(field, "get_raw"):
                return field.get_raw
            return field.getRaw
        return field.get

    @security.private
    def mutator(self, fieldname):
        """Return the field mutator for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        return schema[fieldname].set


@implementer(IItem)
class Item(BaseItem):
    """Base class for SENAITE contentish contents
    """
    security = ClassSecurityInfo()

    @security.private
    def accessor(self, fieldname, raw=False):
        """Return the field accessor for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        field = schema[fieldname]
        if raw:
            if hasattr(field, "get_raw"):
                return field.get_raw
            return field.getRaw
        return field.get

    @security.private
    def mutator(self, fieldname):
        """Return the field mutator for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        return schema[fieldname].set
