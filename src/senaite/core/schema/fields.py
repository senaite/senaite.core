# -*- coding: utf-8 -*-

from bika.lims.api.security import check_permission
from collective.z3cform.datagridfield import DictRow
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from senaite.core.schema.interfaces import IBaseField
from senaite.core.schema.interfaces import IDataGridField
from senaite.core.schema.interfaces import IDataGridRow
from senaite.core.schema.interfaces import IIntField
from zope.interface import implementer
from zope.schema import Field
from zope.schema import Int
from zope.schema import List
from zope.schema._bootstrapfields import _NotGiven


@implementer(IBaseField)
class BaseField(Field):
    """Extensible base field
    """

    def __init__(self, title=u"", description=u"", __name__="",
                 required=True, readonly=False, constraint=None,
                 default=None, defaultFactory=None,
                 missing_value=_NotGiven, **kw):

        # Call superclass with known keywords
        super(BaseField, self).__init__(title=title, description=description,
                                        __name__=__name__,
                                        required=required,
                                        readonly=readonly,
                                        constraint=constraint,
                                        default=default,
                                        defaultFactory=defaultFactory,
                                        missing_value=missing_value)

        # field security
        self.read_permission = kw.get("read_permission", View)
        self.write_permission = kw.get("write_permission", ModifyPortalContent)

    def get(self, object):
        """Custom field getter

        see zope.schem._bootstrapfields.Field
        """
        return super(BaseField, self).get(object)

    def query(self, object, default=None):
        """Custom field query

        see zope.schem._bootstrapfields.Field
        """
        return super(BaseField, self).query(object, default=default)

    def set(self, object, value):
        """Custom field setter

        This place would theoretically allow to set custom "change" events or
        check permissions to write the field.

        see zope.schem._bootstrapfields.Field
        """
        super(BaseField, self).set(object, value)

    def can_access(self):
        """Checks if the field can be read
        """
        return check_permission(self.read_permission, self.context)

    def can_write(self):
        """Checks the write permission
        """
        return check_permission(self.write_permission, self.context)


@implementer(IIntField)
class IntField(Int, BaseField):
    """A field that handles Integer values
    """
    def _validate(self, value):
        super(IntField, self)._validate(value)


@implementer(IDataGridField)
class DataGridField(List, BaseField):
    """A field that stores a list of dictionaries
    """
    def set(self, object, value):
        super(DataGridField, self).set(object, value)


@implementer(IDataGridRow)
class DataGridRow(DictRow, BaseField):
    """A field that stores a data grid row
    """
