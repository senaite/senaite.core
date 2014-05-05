# -*- coding:utf-8 -*-
from bika.lims.interfaces import IWidgetVisibility
from bika.lims.utils import getHiddenAttributesForClass
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.interface import implements


class WidgetVisibility(object):
    """The values returned here do not decide the field order, only their
    visibility.  The field order is set in the schema.
    """
    implements(IWidgetVisibility)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        ret = {}

        fields = list(self.context.Schema().fields())

        # Get optional fields for class
        hiddenattributes = getHiddenAttributesForClass(self.context.portal_type)
        for field in fields:
            if hiddenattributes and \
               field.__name__ in hiddenattributes:
                continue
            if field.widget.visible and isinstance(field.widget.visible, dict):
                for k, v in field.widget.visible.items():
                    if k not in ret:
                        ret[k] = {}
                    if v not in ret[k]:
                        ret[k][v] = []
                    ret[k][v].append(field.getName())

        return ret
