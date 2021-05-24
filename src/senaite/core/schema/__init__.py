# -*- coding: utf-8 -*-

from zope.interface import classImplementsFirst

from .fields import IntField
from .interfaces import IIntField

classImplementsFirst(IntField, IIntField)
