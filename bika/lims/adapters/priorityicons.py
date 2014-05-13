from bika.lims.interfaces import IFieldIcons
from zope.interface import implements

class PriorityIcons(object):

    """An icon provider for indicating AR priorities
    """

    implements(IFieldIcons)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        result = {
            'msg': '',
            'field': 'Priority',
            'icon': '',
        }
        priority = self.context.getPriority()
        if priority:
            result['msg'] = priority.Title()
            icon = priority.getSmallIcon()
            if icon:
                result['icon'] = '/'.join(icon.getPhysicalPath())
            return {self.context.UID(): [result]}
        return {}

