# -*- coding: utf-8 -*-

from senaite.core.schema.fields import BaseField
from senaite.core.schema.interfaces import IUIDReferenceField
from zope.interface import implementer
from zope.schema import ASCIILine
from zope.schema import List
from zope.schema.interfaces import IFromUnicode


@implementer(IUIDReferenceField, IFromUnicode)
class UIDReferenceField(List, BaseField):
    """Stores UID references to other objects
    """

    value_type = ASCIILine(title=u"UID")

    def __init__(self, allowed_types=None, multi_valued=True, **kw):
        self.allowed_types = allowed_types
        self.multi_valued = multi_valued
        super(UIDReferenceField, self).__init__(**kw)

    def set(self, object, value):
        super(UIDReferenceField, self).set(object, value)

    def get(self, object):
        return super(UIDReferenceField, self).get(object)

    def fromUnicode(self, value):
        self.validate(value)
        return value
