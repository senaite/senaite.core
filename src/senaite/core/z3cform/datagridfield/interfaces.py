# -*- coding: utf-8 -*-
#
# Vendored from collective.z3cform.datagridfield 1.5.3.
# See senaite/core/z3cform/datagridfield/__init__.py for details.

from plone.app.z3cform.interfaces import IPloneFormLayer
from z3c.form.interfaces import IMultiWidget
from zope.schema.interfaces import IObject
from zope.schema.interfaces import ValidationError


class IDataGridFieldLayer(IPloneFormLayer):
    """Marker interface that defines a browser layer."""


class IDataGridField(IMultiWidget):
    """Grid widget."""


class AttributeNotFoundError(ValidationError):
    """An attribute is missing from the class"""

    def __init__(self, fieldname, schema):
        self.fieldname = fieldname
        self.schema = schema
        self.__doc__ = u'Missing Field {0} required by schema {1}'.format(
            fieldname,
            schema
        )


class IRow(IObject):
    """A row. The schema defines dict keys.
    """
