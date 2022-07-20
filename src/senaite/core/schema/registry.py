# -*- coding: utf-8 -*-

from senaite.core.schema import RichTextField as BaseRichTextField
from senaite.core.schema.fields import DataGridField as BaseDataGridField
from senaite.core.schema.fields import DataGridRow as BaseDataGridRow
from plone.app.textfield.interfaces import IRichTextValue

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


class RichTextField(PersistentField, BaseRichTextField):
    """Use this field for registry entries

    https://pypi.org/project/plone.registry/#persistent-fields
    https://community.plone.org/t/there-is-no-persistent-field-equivalent-for-the-field-a-of-type-b
    """

    def set(self, object, value):
        """Convert IRichTextValue to plain string for registry

        :param object: the instance of the field
        :param value: value to set
        """
        # Convert value for registry to the raw text
        if IRichTextValue.providedBy(value):
            value = value.raw
        super(RichTextField, self).set(object, value)
