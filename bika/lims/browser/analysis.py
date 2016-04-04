# coding=utf-8
from Products.CMFCore.utils import getToolByName
from bika.lims.jsonapi import get_include_fields
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.utils import t, dicts_to_dict
from bika.lims.interfaces import IAnalysis, IResultOutOfRange, IJSONReadExtender
from bika.lims.interfaces import IFieldIcons
from bika.lims.utils import to_utf8
from bika.lims.utils import dicts_to_dict
import json
import plone
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
                t(_("min")), str(spec.get('min','')),
                t(_("max")), str(spec.get('max','')))
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


class ajaxGetMethodInstrumentConstraints(BrowserView):

    def __call__(self):
        constraints = {}
        try:
            plone.protect.CheckAuthenticator(self.request)
        except Forbidden:
            return json.dumps(constraints)

        uc = getToolByName(self, 'uid_catalog')
        rowuids = self.request.get('uids', '[]')
        rowuids = json.loads(rowuids)
        analyses = uc(portal_type=['Analysis', 'ReferenceAnalysis'],
                      UID=rowuids)
        cached_servs = {}
        for analysis in analyses:
            if not analysis or analysis.portal_type=='ReferenceAnalysis':
                continue
            analysis = analysis.getObject()
            auid = analysis.UID()
            service = analysis.getService()
            suid = service.UID()
            if suid in cached_servs:
                constraints[auid] = cached_servs[suid]
                continue

            refan = analysis.portal_type == 'ReferenceAnalysis'
            dupan = analysis.portal_type == 'DuplicateAnalysis'
            qcan = refan or dupan
            constraints[auid] = {}
            cached_servs[suid] = {}

            # Analysis allows manual/instrument entry?
            s_mentry = service.getManualEntryOfResults()
            s_ientry = service.getInstrumentEntryOfResults()
            s_instrums = service.getRawInstruments() if s_ientry else []
            a_dinstrum = service.getInstrument() if s_ientry else None
            s_methods = service.getAvailableMethods()
            s_dmethod = service.getMethod()
            dmuid = s_dmethod.UID() if s_dmethod else ''
            diuid = a_dinstrum.UID() if a_dinstrum else ''

            # To take into account ASs with no method assigned by default
            if s_mentry:
                s_methods += [None]

            for method in s_methods:
                # Method manual entry?
                m_mentry = method.isManualEntryOfResults() \
                           if method else True

                # Instruments available for this method and analysis?
                instrs = [i for i in method.getInstruments()
                          if i.UID() in s_instrums] if method else []
                v_instrobjs = [i for i in instrs if i.isValid()]
                v_instrs = [i.UID() for i in v_instrobjs]

                # PREMISES
                # p1: Analysis allows manual entry?
                # p2: Analysis allows instrument entry?
                # p3: Method selected and non empty?
                # p4: Method allows manual entry?
                # p5: Valid instruments available?
                # p6: All instruments valid?
                # p7: Default instrument valid?
                premises = [
                    "Y" if s_mentry else "N",
                    "Y" if s_ientry else "N",
                    "Y" if method else "N",
                    "Y" if m_mentry else "N",
                    "Y" if v_instrs or not instrs else "N",
                    "Y" if len(v_instrs) == len(instrs) else "N",
                    "Y" if a_dinstrum and a_dinstrum.isValid() else "N"
                ]
                tprem = ''.join(premises)

                iuid = v_instrs[0] if v_instrs else ''
                iiuid = diuid if diuid in v_instrs else iuid
                muid = method.UID() if method else ''
                instrtitle = a_dinstrum.Title() if a_dinstrum else ''
                m1 = _("Some instruments are not displayed")
                m2 = _("Default instrument %s is not valid") % instrtitle
                m3 = _("No valid instruments available")
                matrix = {
                    'YYYYYY':  [1, 1, muid, 1, 1, iiuid, 1, ''],
                    'YYYYYNY': [1, 1, muid, 1, 1, iiuid, 1, m1],
                    'YYYYYNN': [1, 1, muid, 1, 1, '',    1, m2],
                    'YYYYN':   [1, 1, muid, 1, 1, '',    1, m3],
                    'YYYNYY':  [1, 1, muid, 1, 0, iiuid, 1, ''],
                    'YYYNYNY': [1, 1, muid, 1, 0, iiuid, 1, m1],
                    'YYYNYNN': [1, 1, muid, 1, 1, '',    0, m2],
                    'YYYNN':   [1, 1, muid, 1, 1, '',    0, m3],
                    'YYNYYY':  [1, 1, '',   1, 1, iiuid, 1, ''],
                    'YYNYYNY': [1, 1, '',   1, 1, iiuid, 1, m1],
                    'YYNYYNN': [1, 1, '',   1, 1, '',    1, m2],
                    'YYNYN':   [1, 1, '',   1, 1, '',    1, m3],
                    'YNY':     [2, 0, muid, 0, 1, '',    1, ''],
                    'YNN':     [0, 0, muid, 0, 1, '',    1, ''],
                    'NYYYYY':  [3, 0, muid, 1, 0, iiuid, 1, ''],
                    'NYYYYNY': [3, 0, muid, 1, 0, iiuid, 1, m1],
                    'NYYYYNN': [3, 0, muid, 1, 0, '',    1, m2],
                    'NYYYN':   [3, 0, muid, 1, 1, '',    0, m3],
                    'NYYNYY':  [3, 0, muid, 1, 0, iiuid, 1, ''],
                    'NYYNYNY': [3, 0, muid, 1, 0, iiuid, 1, m1],
                    'NYYNYNN': [3, 0, muid, 1, 1, '',    0, m2],
                    'NYYNN':   [3, 0, muid, 1, 1, '',    0, m3],
                    'NYNYYY':  [3, 1, '',   1, 0, iiuid, 1, ''],
                    'NYNYYNY': [3, 1, '',   1, 0, iiuid, 1, m1],
                    'NYNYYNN': [3, 1, '',   1, 1, '',    0, m2],
                    'NYNYN':   [3, 1, '',   1, 1, '',    0, m3],
                }
                targ = [v for k, v in matrix.items() if tprem.startswith(k)][0]
                atitle = analysis.Title() if analysis else "None"
                mtitle = method.Title() if method else "None"
                instdi = {i.UID(): i.Title() for i in v_instrobjs} if v_instrobjs else {}
                targ += [instdi, mtitle, atitle, tprem]
                constraints[auid][muid] = targ
                cached_servs[suid][muid] = targ

        return json.dumps(constraints)
