# -*- coding: utf-8 -*-

from senaite.core.schema.fields import DataGridField as BaseDataGridField
from senaite.core.schema.fields import DataGridRow as BaseDataGridRow

try:
    from plone.registry.field import PersistentField
except ImportError:
    class PersistentField(object):
        pass


class DataGridField(PersistentField, BaseDataGridField):
    """Use this field for registry entries

    https://pypi.org/project/plone.registry/#persistent-fields
    https://community.plone.org/t/there-is-no-persistent-field-equivalent-for-the-field-a-of-type-b
    """
    pass


class DataGridRow(PersistentField, BaseDataGridRow):
    """Use this field for registry entries

    https://pypi.org/project/plone.registry/#persistent-fields
    https://community.plone.org/t/there-is-no-persistent-field-equivalent-for-the-field-a-of-type-b
    """
    pass
