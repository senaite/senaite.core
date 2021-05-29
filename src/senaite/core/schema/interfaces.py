# -*- coding: utf-8 -*-

from zope.schema.interfaces import IInt
from zope.schema.interfaces import IField


class IBaseField(IField):
    """Senaite base field
    """


class IIntField(IInt):
    """Senaite integer field
    """
