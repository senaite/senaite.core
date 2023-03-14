# -*- coding: utf-8 -*-

from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.Field import LinesField
from senaite.core.api import label as label_api


class ExtLabelField(ExtensionField, LinesField):
    """Extended Field for Labels
    """
    def get(self, instance, **kw):
        labels = label_api.get_obj_labels(instance)
        return labels

    def set(self, instance, value, **kw):
        labels = value.split("\r\n")
        label_api.add_obj_labels(instance, labels)
