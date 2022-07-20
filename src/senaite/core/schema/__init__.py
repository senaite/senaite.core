# -*- coding: utf-8 -*-

from zope.interface import classImplementsFirst

from .addressfield import AddressField
from .addressfield import IAddressField
from .datetimefield import DatetimeField
from .fields import IntField
from .interfaces import IDatetimeField
from .interfaces import IIntField
from .interfaces import IRichTextField
from .richtextfield import RichTextField
from .uidreferencefield import IUIDReferenceField
from .uidreferencefield import UIDReferenceField

classImplementsFirst(AddressField, IAddressField)
classImplementsFirst(DatetimeField, IDatetimeField)
classImplementsFirst(IntField, IIntField)
classImplementsFirst(RichTextField, IRichTextField)
classImplementsFirst(UIDReferenceField, IUIDReferenceField)
