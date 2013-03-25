# -*- coding:utf-8 -*-
from bika.lims.interfaces import IWidgetVisibility
from zope.interface import implements


class WidgetVisibility(object):
    implements(IWidgetVisibility)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        ret = {}

        fields = list(self.context.Schema().fields())

        for field in fields:
            if field.widget.visible and isinstance(field.widget.visible, dict):
                for k, v in field.widget.visible.items():
                    if k not in ret:
                        ret[k] = {}
                    if v not in ret[k]:
                        ret[k][v] = []
                    ret[k][v].append(field.getName())

        return ret
