# coding=utf-8
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IWorksheet
from operator import itemgetter
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.component import getAdapters
from zope.interface import implements


class ResultOutOfRangeAdapter(object):
    """Return alerts for any analyses inside the context worksheet
    """
    implements(IFieldIcons)
    adapts(IWorksheet)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, **kwargs):
        workflow = getToolByName(self.context, 'portal_workflow')
        items = self.context.getAnalyses()
        field_icons = {}
        for obj in items:
            obj = obj.getObject() if hasattr(obj, 'getObject') else obj
            uid = obj.UID()
            astate = workflow.getInfoFor(obj, 'review_state')
            if astate == 'retracted':
                continue
            adapters = getAdapters((obj, ), IFieldIcons)
            for name, adapter in adapters:
                alerts = adapter()
                if alerts:
                    if uid in field_icons:
                        field_icons[uid].extend(alerts[uid])
                    else:
                        field_icons[uid] = alerts[uid]
        return field_icons
