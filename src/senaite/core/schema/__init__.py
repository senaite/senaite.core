# -*- coding: utf-8 -*-

from zope.interface import classImplementsFirst

from .datetimefield import DatetimeField
from .fields import IntField
from .interfaces import IDatetimeField
from .interfaces import IIntField
from .uidreferencefield import IUIDReferenceField
from .uidreferencefield import UIDReferenceField
from .addressfield import IAddressField
from .addressfield import AddressField

classImplementsFirst(IntField, IIntField)
classImplementsFirst(UIDReferenceField, IUIDReferenceField)
classImplementsFirst(DatetimeField, IDatetimeField)
classImplementsFirst(AddressField, IAddressField)
