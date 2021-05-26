# -*- coding: utf-8 -*-

from collective.z3cform.datagridfield.interfaces import IRow
from zope.schema.interfaces import IField
from zope.schema.interfaces import IInt
from zope.schema.interfaces import IList


class IBaseField(IField):
    """Senaite base field
    """


class IIntField(IInt):
    """Senaite integer field
    """


class IDataGridField(IList):
    """Senaite datagrid field
    """


class IDataGridRow(IRow):
    """Datagrid row
    """
