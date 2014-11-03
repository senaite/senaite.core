# coding=utf-8
from Products.CMFCore.utils import getToolByName
from bika.lims.jsonapi import get_include_fields
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t, dicts_to_dict
from bika.lims.interfaces import IAnalysis, IResultOutOfRange, IJSONReadExtender
from bika.lims.interfaces import IFieldIcons
from bika.lims.utils import to_utf8
from bika.lims.utils import dicts_to_dict
from zope.component import adapts, getAdapters
from zope.interface import implements


class ResultOutOfRangeIcons(object):
    """An icon provider for Analyses: Result field out-of-range alerts
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, **kwargs):
        translate = self.context.translate
        path = '++resource++bika.lims.images'
        alerts = {}
        # We look for IResultOutOfRange adapters for this object
        for name, adapter in getAdapters((self.context, ), IResultOutOfRange):
            ret = adapter(result)
            if not ret:
                continue
            spec = ret["spec_values"]
            rngstr = "{0} {1}, {2} {3}".format(
                t(_("min")), str(spec['min']),
                t(_("max")), str(spec['max']))
            if ret["out_of_range"]:
                if ret["acceptable"]:
                    message = "{0} ({1})".format(
                        t(_('Result in shoulder range')),
                        rngstr
                    )
                    icon = path + '/warning.png'
                else:
                    message = "{0} ({1})".format(
                        t(_('Result out of range')),
                        rngstr
                    )
                    icon = path + '/exclamation.png'
                alerts[self.context.UID()] = [
                    {
                        'icon': icon,
                        'msg': message,
                        'field': 'Result',
                    },
                ]
                break
        return alerts


class ResultOutOfRange(object):
    """Check if results are within tolerated values
    """

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, specification=None):
        workflow = getToolByName(self.context, 'portal_workflow')
        astate = workflow.getInfoFor(self.context, 'review_state')
        if astate == 'retracted':
            return None
        result = result is not None and str(result) or self.context.getResult()
        if result == '':
            return None
        # if analysis result is not a number, then we assume in range:
        try:
            result = float(str(result))
        except ValueError:
            return None
        # The spec is found in the parent AR's ResultsRange field.
        if not specification:
            rr = dicts_to_dict(self.context.aq_parent.getResultsRange(), 'keyword')
            specification = rr.get(self.context.getKeyword(), None)
            # No specs available, assume in range:
            if not specification:
                return None
        outofrange, acceptable = \
            self.isOutOfRange(result,
                              specification.get('min', ''),
                              specification.get('max', ''),
                              specification.get('error', ''))
        return {
            'out_of_range': outofrange,
            'acceptable': acceptable,
            'spec_values': specification
        }



    def isOutOfShoulderRange(self, result, Min, Max, error):
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


    def isOutOfRange(self, result, Min, Max, error):
        spec_min = None
        spec_max = None
        try:
            result = float(result)
        except:
            return False, False
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
            if self.isOutOfShoulderRange(result, Min, Max, error):
                return True, True
            else:
                return False, False  # No Min and Max values defined
        elif spec_min is not None and spec_max is not None and spec_min <= result <= spec_max:
            if self.isOutOfShoulderRange(result, Min, Max, error):
                return True, True
            else:
                return False, False  # Min and Max values defined
        elif spec_min is not None and spec_max is None and spec_min <= result:
            if self.isOutOfShoulderRange(result, Min, Max, error):
                return True, True
            else:
                return False, False  # Max value not defined
        elif spec_min is None and spec_max is not None and spec_max >= result:
            if self.isOutOfShoulderRange(result, Min, Max, error):
                return True, True
            else:
                return False, False  # Min value not defined
        if self.isOutOfShoulderRange(result, Min, Max, error):
            return True, True
        return True, False
    
class JSONReadExtender(object):

    """- Adds the specification from Analysis Request to Analysis in JSON response
    """

    implements(IJSONReadExtender)
    adapts(IAnalysis)

    def __init__(self, context):
        self.context = context

    def analysis_specification(self):
        ar = self.context.aq_parent
        rr = dicts_to_dict(ar.getResultsRange(),'keyword')
        
        return rr[self.context.getService().getKeyword()]

    def __call__(self, request, data):
        self.request = request
        self.include_fields = get_include_fields(request)
        if not self.include_fields or "specification" in self.include_fields:
            data['specification'] = self.analysis_specification()
        return data


