# coding=utf-8
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IFieldIcons
from bika.lims.permissions import *
from zope.component import adapts
from zope.interface import implements


class ResultOutOfRange(object):

    """An icon provider for DuplicateAnalysis: Result field out-of-range alerts
    """
    implements(IFieldIcons)
    adapts(IAnalysis)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, specification=None, **kwargs):
        # Other types of analysis depend on Analysis base class, and therefore
        # also provide IAnalysis.  We allow them to register their own adapters
        # for range checking, and manually ignore them here.
        if self.context.portal_type != 'DuplicateAnalysis':
            return {}
        workflow = getToolByName(self.context, 'portal_workflow')
        astate = workflow.getInfoFor(self.context, 'review_state')
        if astate == 'retracted':
            return {}
        result = result is not None and str(result) or self.context.getResult()
        # We get the form_result for our duplicated analysis in **kwargs[orig]
        # If not, then use the database value.
        if 'form_results' in kwargs:
            auid = self.context.getAnalysis().UID()
            orig = kwargs.get('form_results', {}).get(auid)
        else:
            orig = self.context.getAnalysis().getResult()
        try:
            result = float(str(result))
            orig = float(str(orig))
            variation = float(self.context.getService().getDuplicateVariation())
        except ValueError:
            return {}

        range_min = orig - (orig * variation / 100)
        range_max = orig + (orig * variation / 100)
        if range_min <= result <= range_max:
            return {}
        else:
            translate = self.context.translate
            path = "++resource++bika.lims.images"
            message = "{0} ({1} {2}, {3} {4})".format(
                translate(_('Result out of range')),
                translate(_("min")), str(range_min),
                translate(_("max")), str(range_max))
            return {self.context.UID(): [{
                'msg': message,
                'field': 'Result',
                'icon': path + '/exclamation.png',
            }, ]}
