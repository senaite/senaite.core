# -*- coding: utf-8 -*-

from archetypes.schemaextender.field import ExtensionField
from bika.lims import api
from Products.Archetypes.Field import LinesField
from senaite.core.api import label as label_api


class ExtLabelField(ExtensionField, LinesField):
    """Extended Field for Labels
    """
    def get(self, instance, **kw):
        labels = label_api.get_obj_labels(instance)
        return labels

    def set(self, instance, value, **kw):
        if api.is_string(value):
            value = filter(None, value.split("\r\n"))
        labels = label_api.to_labels(value)
        return label_api.set_obj_labels(instance, labels)
