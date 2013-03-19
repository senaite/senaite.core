# -*- coding:utf-8 -*-
from bika.lims.interfaces import IWidgetVisibility
from zope.interface import implements


class WidgetVisibility(object):
    implements(IWidgetVisibility)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        ret = {'view': {'visible': [], 'invisible': [], 'hidden': [], },
               'edit': {'visible': [], 'invisible': [], 'hidden': [], },
               'add': {'visible': [], 'invisible': [], 'hidden': []}}

        if 'schema' in kwargs:
            fields = list(kwargs['schema'].fields())
        else:
            fields = list(self.context.Schema().fields())

        for field in fields:
            if field.widget.visible and isinstance(field.widget.visible, dict):
                for k, v in field.widget.visible.items():
                    ret[k][v].append(field.getName())

        return ret
