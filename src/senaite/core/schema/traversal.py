# -*- coding: utf-8 -*-

from bika.lims import api
from plone.dexterity.utils import resolveDottedName
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError


@adapter(Interface, IBrowserRequest)
@implementer(ITraversable)
class FieldTraversal(object):
    """Allow to traverse schema fields via the ++field++ namespace.
    """
    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        if "." in name:
            # we expect the dotted schema interface + the fieldname
            iface, fieldname = name.rsplit(".", 1)
            schema = resolveDottedName(iface)
            field = schema.get(fieldname)
        else:
            fields = api.get_fields(self.context)
            field = fields.get(name)
        if not field:
            raise TraversalError(name)
        field = field.bind(self.context)
        return field
