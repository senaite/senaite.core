# coding=utf-8
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IFieldIcons
from zope.component import adapts
from zope.interface import implements
from bika.lims.utils import isnumber


def isOutOfShoulderRange(result, spec, keyword):
    # check if in 'shoulder' range - out of range, but in acceptable error
    spec_min = spec[keyword].get('min', '')
    spec_min = float(spec_min) if isnumber(spec_min) else None
    spec_max = spec[keyword].get('max', '')
    spec_max = float(spec_max) if isnumber(spec_max) else None
    error = 0
    try:
        error = float(spec[keyword].get('error', '0'))
    except:
        pass
    error_amount = (result / 100) * error
    error_min = result - error_amount
    error_max = result + error_amount
    if (spec_min and result < spec_min and error_max >= spec_min) \
        or (spec_max and result > spec_max and error_min <= spec_max):
        return True
    # Default: in range
    return False


def isOutOfRange(result, spec, keyword):
    spec_min = None
    spec_max = None
    try:
        spec_min = float(spec[keyword]['min'])
    except:
        spec_min = None
        pass
    try:
        spec_max = float(spec[keyword]['max'])
    except:
        spec_max = None
        pass
    if (not spec_min and not spec_max):
        if isOutOfShoulderRange(result, spec, keyword):
            return True, True, spec[keyword]
        else:
            return False, None, None  # No min and max values defined
    elif spec_min and spec_max and spec_min <= result <= spec_max:
        if isOutOfShoulderRange(result, spec, keyword):
            return True, True, spec[keyword]
        else:
            return False, None, None  # min and max values defined
    elif spec_min and not spec_max and spec_min <= result:
        if isOutOfShoulderRange(result, spec, keyword):
            return True, True, spec[keyword]
        else:
            return False, None, None  # max value not defined
    elif not spec_min and spec_max and spec_max >= result:
        if isOutOfShoulderRange(result, spec, keyword):
            return True, True, spec[keyword]
        else:
            return False, None, None  # min value not defined
    if isOutOfShoulderRange(result, spec, keyword):
        return True, True, spec[keyword]
    return True, None, spec[keyword]


class ResultOutOfRange(object):

    """An icon provider for Analyses: Result field out-of-range alerts
    """
    implements(IFieldIcons)
    adapts(IAnalysis)

    def __init__(self, context):
        self.context = context

    def get_alerts(self, outofrange, acceptable, o_spec, **kwargs):
        alerts = {}
        translate = self.context.translate
        path = '++resource++bika.lims.images'
        if outofrange:
            rngstr = "{0} {1}, {2}, {3}".format(
                translate(_("min")), str(o_spec.get('min', '')),
                translate(_("max")), str(o_spec.get('max', '')))

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

    def __call__(self, result=None, specification="lab", **kwargs):
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

        # No specs available, assume in range:
        specs = self.context.getAnalysisSpecs(specification)
        if specs is None:
            return {}
        keyword = self.context.getService().getKeyword()
        spec = specs.getResultsRangeDict()
        if keyword in spec:
            outofrange, acceptable, o_spec = isOutOfRange(result, spec, keyword)
            return self.get_alerts(outofrange, acceptable, o_spec)
        else:
            # Analysis without specification values. Assume in range
            return {}
