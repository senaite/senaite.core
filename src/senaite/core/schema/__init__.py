# -*- coding: utf-8 -*-

from zope.interface import classImplementsFirst

from .fields import IntField
from .interfaces import IIntField
from .uidreferencefield import IUIDReferenceField
from .uidreferencefield import UIDReferenceField

classImplementsFirst(IntField, IIntField)
classImplementsFirst(UIDReferenceField, IUIDReferenceField)
