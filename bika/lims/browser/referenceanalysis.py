# coding=utf-8
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IFieldIcons
from bika.lims.permissions import *
from zope.component import adapts
from zope.interface import implements


class ResultOutOfRange(object):

    """An icon provider for Analyses: Result field out-of-range alerts
    """
    implements(IFieldIcons)
    adapts(IAnalysis)

    def __init__(self, context):
        self.context = context

    def get_alerts(self, outofrange, acceptable, spec):
        alerts = {}
        translate = self.context.translate
        path = '++resource++bika.lims.images'
        if outofrange:
            rngstr = "{0} {1}, {2}, {3}".format(
                translate(_("min")), str(spec['min']),
                translate(_("max")), str(spec['max']))

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

    def __call__(self, result=None, specification=None, **kwargs):
        # Other types of analysis depend on Analysis base class, and therefore
        # also provide IAnalysis.  We allow them to register their own adapters
        # for range checking, and manually ignore them here.
        if self.context.portal_type != 'ReferenceAnalysis':
            return {}
        workflow = getToolByName(self.context, 'portal_workflow')
        astate = workflow.getInfoFor(self.context, 'review_state')
        if astate == 'retracted':
            return {}
        result = result is not None and str(result) or self.context.getResult()
        try:
            result = float(str(result))
        except ValueError:
            return {}
        service_uid = self.context.getService().UID()
        spec = self.context.aq_parent.getResultsRangeDict()
        if service_uid in spec:
            spec_min = None
            spec_max = None
            try:
                spec_min = float(spec[service_uid]['min'])
            except:
                spec_min = None
                pass
            try:
                spec_max = float(spec[service_uid]['max'])
            except:
                spec_max = None
                pass
            if (spec_min==0 and spec_max==0 and result !=0):
                # Value has to be zero
                outofrange, acceptable, o_spec = True, False, spec[service_uid]
            elif (not spec_min and not spec_max):
                # No min and max values defined
                outofrange, acceptable, o_spec = False, None, None
            elif spec_min and spec_max and spec_min <= result <= spec_max:
                # min and max values defined
                outofrange, acceptable, o_spec = False, None, None
            elif spec_min and not spec_max and spec_min <= result:
                # max value not defined
                outofrange, acceptable, o_spec = False, None, None
            elif not spec_min and spec_max and spec_max >= result:
                # min value not defined
                outofrange, acceptable, o_spec = False, None, None
            else:
                outofrange, acceptable, o_spec = True, False, spec[service_uid]

            if not outofrange:
                """ check if in 'shoulder' error range - out of range,
                    but in acceptable error """
                error = 0
                try:
                    error = float(spec[service_uid].get('error', '0'))
                except:
                    error = 0
                    pass
                error_amount = (result / 100) * error
                error_min = result - error_amount
                error_max = result + error_amount
                if (spec_min and result < spec_min and error_max >= spec_min) \
                        or (spec_max and result > spec_max and error_min <= spec_max):
                    outofrange, acceptable, o_spec = True, True, spec[service_uid]
            return self.get_alerts(outofrange, acceptable, o_spec)
        else:
            # Analysis without specification values. Assume in range
            return {}
