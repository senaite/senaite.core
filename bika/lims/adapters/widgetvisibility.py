# -*- coding:utf-8 -*-
from bika.lims.interfaces import IWidgetVisibility
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.interface import implements


class WidgetVisibility(object):
    implements(IWidgetVisibility)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        ret = {}

        fields = list(self.context.Schema().fields())

        # Get optional fields for class
        optionally_disabled_fields = ()
        try:
            registry = queryUtility(IRegistry)
            hiddenattributes = registry.get('bika.lims.hiddenattributes', ())
            for alist in hiddenattributes:
                if alist[0] == self.context.portal_type:
                    optionally_disabled_fields = alist[1:]
                    break
        except:
            pass

        print 'Root adapter'
        for field in fields:
            if optionally_disabled_fields and \
               field.__name__ in optionally_disabled_fields:
                continue
            if field.widget.visible and isinstance(field.widget.visible, dict):
                for k, v in field.widget.visible.items():
                    if k not in ret:
                        ret[k] = {}
                    if v not in ret[k]:
                        ret[k][v] = []
                    ret[k][v].append(field.getName())

        print 'Root: %s' % str(ret.keys())
        return ret
