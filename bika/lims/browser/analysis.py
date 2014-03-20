# coding=utf-8
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IFieldIcons
from bika.lims.permissions import *
from zope.component import adapts
from zope.interface import implements


def isOutOfShoulderRange(result, Min, Max, error):
    # check if in 'shoulder' range - out of range, but in acceptable error
    spec_min = None
    spec_max = None
    try:
        result = float(result)
    except:
        return False, None
    try:
        spec_min = float(Min)
    except:
        spec_min = None
    try:
        error = float(error)
    except:
        error = 0
    try:
        spec_max = float(Max)
    except:
        spec_max = None
    error_amount = (result / 100) * error
    error_min = result - error_amount
    error_max = result + error_amount
    if (spec_min and result < spec_min and error_max >= spec_min) \
            or (spec_max and result > spec_max and error_min <= spec_max):
        return True
    # Default: in range
    return False


def isOutOfRange(result, Min, Max, error):
    spec_min = None
    spec_max = None
    try:
        result = float(result)
    except:
        return False, None
    try:
        spec_min = float(Min)
    except:
        spec_min = None
    try:
        error = float(error)
    except:
        error = 0
    try:
        spec_max = float(Max)
    except:
        spec_max = None
    if (spec_min is None and spec_max is None):
        if isOutOfShoulderRange(result, Min, Max, error):
            return True, True
        else:
            return False, None  # No Min and Max values defined
    elif spec_min is not None and spec_max is not None and spec_min <= result <= spec_max:
        if isOutOfShoulderRange(result, Min, Max, error):
            return True, True
        else:
            return False, None  # Min and Max values defined
    elif spec_min is not None and spec_max is None and spec_min <= result:
        if isOutOfShoulderRange(result, Min, Max, error):
            return True, True
        else:
            return False, None  # Max value not defined
    elif spec_min is None and spec_max is not None and spec_max >= result:
        if isOutOfShoulderRange(result, Min, Max, error):
            return True, True
        else:
            return False, None  # Min value not defined
    if isOutOfShoulderRange(result, Min, Max, error):
        return True, True
    return True, None


class ResultOutOfRange(object):

    """An icon provider for Analyses: Result field out-of-range alerts
    """
    implements(IFieldIcons)
    adapts(IAnalysis)

    def __init__(self, context):
        self.context = context

    def get_alerts(self, outofrange, acceptable, Min, Max):
        alerts = {}
        translate = self.context.translate
        path = '++resource++bika.lims.images'
        if outofrange:
            rngstr = "{0} {1}, {2} {3}".format(
                translate(_("min")), str(Min),
                translate(_("max")), str(Max))

            if acceptable:
                message = "{0} ({1})".format(
                    translate(_('Result in shoulder range')), rngstr)
            else:
                message = "{0} ({1})".format(
                    translate(_('Result out of range')), rngstr)

            alerts[self.context.UID()] = [{
                'icon': path + '/warning.png' if acceptable else
                path + '/exclamation.png',
                'msg': message,
                'field': 'Result',
            }, ]
        return alerts

    def __call__(self, result=None, **kwargs):
        # Other types of analysis depend on Analysis base class, and therefore
        # also provide IAnalysis.  We allow them to register their own adapters
        # for range checking, and manually ignore them here.
        ignore = ('ReferenceAnalysis', 'DuplicateAnalysis')
        if self.context.portal_type in ignore:
            return {}
        # Retracted analyses don't qualify
        workflow = getToolByName(self.context, 'portal_workflow')
        astate = workflow.getInfoFor(self.context, 'review_state')
        if astate == 'retracted':
            return {}
        result = result is not None and str(result) or self.context.getResult()
        if result == '':
            return {}
        # if analysis result is not a number, then we assume in range:
        try:
            result = float(str(result))
        except ValueError:
            return {}

        spec = {}
        if hasattr(self.context, "specification") and self.context.specification:
            spec = self.context.specification
        if 'specification' in kwargs:
            spec = kwargs['specification']
        if not spec:
            # No specs available, assume in range:
            return {}

        outofrange, acceptable = isOutOfRange(result,
                                              spec.get('min', ''),
                                              spec.get('max', ''),
                                              spec.get('error', ''))
        return self.get_alerts(outofrange,
                               acceptable,
                               spec.get('min', ''),
                               spec.get('max', ''))
