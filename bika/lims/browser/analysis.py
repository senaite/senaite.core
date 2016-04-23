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
        """
            Returns a json dictionary with the constraints and rules for
            methods, instruments and results to be applied to each of the
            analyses specified in the request (an array of uids).
            See docs/imm_results_entry_behaviour.png for further details
        """
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
            if not analysis:
                continue
            analysis = analysis.getObject()
            auid = analysis.UID()
            service = analysis.getService()
            suid = service.UID()
            refan = analysis.portal_type == 'ReferenceAnalysis'
            cachedkey = "qc" if refan else "re"
            if suid in cached_servs.get(cachedkey, []):
                constraints[auid] = cached_servs[cachedkey][suid]
                continue

            if not cached_servs.get(cachedkey, None):
                cached_servs[cachedkey] = {suid: {}}
            else:
                cached_servs[cachedkey][suid] = {}
            constraints[auid] = {}

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
                instuids = [i.UID() for i in instrs]
                v_instrobjs = [i for i in instrs if i.isValid()]
                v_instrs = [i.UID() for i in v_instrobjs]
                muid = method.UID() if method else ''

                # PREMISES
                # p1: Analysis allows manual entry?
                # p2: Analysis allows instrument entry?
                # p3: Method selected and non empty?
                # p4: Method allows manual entry?
                # p5: At least one instrument available for this method?
                # p6: Valid instruments available?
                # p7: All instruments valid?
                # p8: Methods allow the service's default instrument?
                # p9: Default instrument valid?
                premises = [
                    "R" if not refan else 'Q',
                    "Y" if s_mentry else "N",
                    "Y" if s_ientry else "N",
                    "Y" if method else "N",
                    "Y" if m_mentry else "N",
                    "Y" if instrs else "N",
                    "Y" if v_instrs or not instrs else "N",
                    "Y" if len(v_instrs) == len(instrs) else "N",
                    "Y" if diuid in instuids else "N",
                    "Y" if a_dinstrum and a_dinstrum.isValid() else "N",
                ]
                tprem = ''.join(premises)

                fiuid = v_instrs[0] if v_instrs else ''
                instrtitle = a_dinstrum.Title() if a_dinstrum else ''
                iinstrs = ', '.join([i.Title() for i in instrs
                                    if i.UID() not in v_instrs])
                dmeth = method.Title() if method else ''
                m1 = _("Invalid instruments are not displayed: %s") % iinstrs
                m2 = _("Default instrument %s is not valid") % instrtitle
                m3 = _("No valid instruments available: %s ") % iinstrs
                m4 = _("Manual entry of results for method %s is not allowed "
                       "and no valid instruments found: %s") % (dmeth, iinstrs)
                m5 = _("The method %s is not valid: no manual entry allowed "
                       "and no instrument assigned") % dmeth
                m6 = _("The method %s is not valid: only instrument entry for "
                       "this analysis is allowed, but the method has no "
                       "instrument assigned") % dmeth
                m7 = _("Only instrument entry for this analysis is allowed, "
                       "but there is no instrument assigned")

                """
                Matrix dict keys char positions: (True: Y, False: N)
                  0: (R)egular analysis or (Q)C analysis
                  1: Analysis allows manual entry?
                  2: Analysis allows instrument entry?
                  3: Method is not None?
                  4: Method allows manual entry?
                  5: At least one instrument avialable for the method?
                  6: Valid instruments available?
                  7: All instruments valid?
                  8: Method allows the service's default instrument?
                  9: Default instrument valid?

                Matrix dict values array indexes:
                  0: Method list visible? YES:1, NO:0, YES(a):2, YES(r):3
                  1: Add "None" in methods list? YES:1, NO:0, NO(g):2
                  2: Instr. list visible? YES:1, NO:0
                  3: Add "None" in instrums list? YES: 1, NO:0
                  4: UID of the selected instrument or '' if None
                  5: Results field editable? YES: 1, NO:0
                  6: Alert message string

                See docs/imm_results_entry_behaviour.png for further details
                """
                matrix = {
                    # Regular analyses
                    'RYYYYYYYY':  [1, 1, 1, 1, diuid, 1, ''],  # B1
                    'RYYYYYYYN':  [1, 1, 1, 1, '',    1, ''],  # B2
                    'RYYYYYYNYY': [1, 1, 1, 1, diuid, 1, m1],  # B3
                    'RYYYYYYNYN': [1, 1, 1, 1, '',    1, m2],  # B4
                    'RYYYYYYNN':  [1, 1, 1, 1, '',    1, m1],  # B5
                    'RYYYYYN':    [1, 1, 1, 1, '',    1, m3],  # B6
                    'RYYYYN':     [1, 1, 1, 1, '',    1, ''],  # B7
                    'RYYYNYYYY':  [1, 1, 1, 0, diuid, 1, ''],  # B8
                    'RYYYNYYYN':  [1, 1, 1, 0, fiuid, 1, ''],  # B9
                    'RYYYNYYNYY': [1, 1, 1, 0, diuid, 1, m1],  # B10
                    'RYYYNYYNYN': [1, 1, 1, 1, '',    0, m2],  # B11
                    'RYYYNYYNN':  [1, 1, 1, 0, fiuid, 1, m1],  # B12
                    'RYYYNYN':    [1, 1, 1, 1, '',    0, m4],  # B13
                    'RYYYNN':     [1, 1, 1, 1, '',    0, m5],  # B14
                    'RYYNYYYYY':  [1, 1, 1, 1, diuid, 1, ''],  # B15
                    'RYYNYYYYN':  [1, 1, 1, 1, '',    1, ''],  # B16
                    'RYYNYYYNYY': [1, 1, 1, 1, diuid, 1, m1],  # B17
                    'RYYNYYYNYN': [1, 1, 1, 1, '',    1, m2],  # B18
                    'RYYNYYYNN':  [1, 1, 1, 1, '',    1, m1],  # B19
                    'RYYNYYN':    [1, 1, 1, 1, '',    1, m3],  # B20
                    'RYYNYN':     [1, 1, 1, 1, '',    1, ''],  # B21
                    'RYNY':       [2, 0, 0, 0, '',    1, ''],  # B22
                    'RYNN':       [0, 0, 0, 0, '',    1, ''],  # B23
                    'RNYYYYYYY':  [3, 2, 1, 1, diuid, 1, ''],  # B24
                    'RNYYYYYYN':  [3, 2, 1, 1, '',    1, ''],  # B25
                    'RNYYYYYNYY': [3, 2, 1, 1, diuid, 1, m1],  # B26
                    'RNYYYYYNYN': [3, 2, 1, 1, '',    1, m2],  # B27
                    'RNYYYYYNN':  [3, 2, 1, 1, '',    1, m1],  # B28
                    'RNYYYYN':    [3, 2, 1, 1, '',    1, m3],  # B29
                    'RNYYYN':     [3, 2, 1, 1, '',    0, m6],  # B30
                    'RNYYNYYYY':  [3, 2, 1, 0, diuid, 1, ''],  # B31
                    'RNYYNYYYN':  [3, 2, 1, 0, fiuid, 1, ''],  # B32
                    'RNYYNYYNYY': [3, 2, 1, 0, diuid, 1, m1],  # B33
                    'RNYYNYYNYN': [3, 2, 1, 1, '',    0, m2],  # B34
                    'RNYYNYYNN':  [3, 2, 1, 0, fiuid, 1, m1],  # B35
                    'RNYYNYN':    [3, 2, 1, 1, '',    0, m3],  # B36
                    'RNYYNN':     [3, 2, 1, 1, '',    0, m6],  # B37
                    'RNYNYYYYY':  [3, 1, 1, 0, diuid, 1, ''],  # B38
                    'RNYNYYYYN':  [3, 1, 1, 0, fiuid, 1, ''],  # B39
                    'RNYNYYYNYY': [3, 1, 1, 0, diuid, 1, m1],  # B40
                    'RNYNYYYNYN': [3, 1, 1, 1, '',    0, m2],  # B41
                    'RNYNYYYNN':  [3, 1, 1, 0, fiuid, 1, m1],  # B42
                    'RNYNYYN':    [3, 1, 1, 0, '',    0, m3],  # B43
                    'RNYNYN':     [3, 1, 1, 0, '',    0, m7],  # B44
                    # QC Analyses
                    'QYYYYYYYY':  [1, 1, 1, 1, diuid, 1, ''],  # C1
                    'QYYYYYYYN':  [1, 1, 1, 1, '',    1, ''],  # C2
                    'QYYYYYYNYY': [1, 1, 1, 1, diuid, 1, ''],  # C3
                    'QYYYYYYNYN': [1, 1, 1, 1, diuid, 1, ''],  # C4
                    'QYYYYYYNN':  [1, 1, 1, 1, '',    1, ''],  # C5
                    'QYYYYYN':    [1, 1, 1, 1, '',    1, ''],  # C6
                    'QYYYYN':     [1, 1, 1, 1, '',    1, ''],  # C7
                    'QYYYNYYYY':  [1, 1, 1, 0, diuid, 1, ''],  # C8
                    'QYYYNYYYN':  [1, 1, 1, 0, fiuid, 1, ''],  # C9
                    'QYYYNYYNYY': [1, 1, 1, 0, diuid, 1, ''],  # C10
                    'QYYYNYYNYN': [1, 1, 1, 0, diuid, 1, ''],  # C11
                    'QYYYNYYNN':  [1, 1, 1, 0, fiuid, 1, ''],  # C12
                    'QYYYNYN':    [1, 1, 1, 0, fiuid, 1, ''],  # C13
                    'QYYYNN':     [1, 1, 1, 1, '',    0, m5],  # C14
                    'QYYNYYYYY':  [1, 1, 1, 1, diuid, 1, ''],  # C15
                    'QYYNYYYYN':  [1, 1, 1, 1, '',    1, ''],  # C16
                    'QYYNYYYNYY': [1, 1, 1, 1, diuid, 1, ''],  # C17
                    'QYYNYYYNYN': [1, 1, 1, 1, diuid, 1, ''],  # C18
                    'QYYNYYYNN':  [1, 1, 1, 1, fiuid, 1, ''],  # C19
                    'QYYNYYN':    [1, 1, 1, 1, diuid, 1, ''],  # C20
                    'QYYNYN':     [1, 1, 1, 1, '',    1, ''],  # C21
                    'QYNY':       [2, 0, 0, 0, '',    1, ''],  # C22
                    'QYNN':       [0, 0, 0, 0, '',    1, ''],  # C23
                    'QNYYYYYYY':  [3, 2, 1, 1, diuid, 1, ''],  # C24
                    'QNYYYYYYN':  [3, 2, 1, 1, '',    1, ''],  # C25
                    'QNYYYYYNYY': [3, 2, 1, 1, diuid, 1, ''],  # C26
                    'QNYYYYYNYN': [3, 2, 1, 1, diuid, 1, ''],  # C27
                    'QNYYYYYNN':  [3, 2, 1, 1, '',    1, ''],  # C28
                    'QNYYYYN':    [3, 2, 1, 1, '',    1, ''],  # C29
                    'QNYYYN':     [3, 2, 1, 1, '',    0, m6],  # C30
                    'QNYYNYYYY':  [3, 2, 1, 0, diuid, 1, ''],  # C31
                    'QNYYNYYYN':  [3, 2, 1, 0, fiuid, 1, ''],  # C32
                    'QNYYNYYNYY': [3, 2, 1, 0, diuid, 1, ''],  # C33
                    'QNYYNYYNYN': [3, 2, 1, 0, diuid, 1, ''],  # C34
                    'QNYYNYYNN':  [3, 2, 1, 0, fiuid, 1, ''],  # C35
                    'QNYYNYN':    [3, 2, 1, 0, fiuid, 1, ''],  # C36
                    'QNYYNN':     [3, 2, 1, 1, '',    0, m5],  # C37
                    'QNYNYYYYY':  [3, 1, 1, 0, diuid, 1, ''],  # C38
                    'QNYNYYYYN':  [3, 1, 1, 0, fiuid, 1, ''],  # C39
                    'QNYNYYYNYY': [3, 1, 1, 0, diuid, 1, ''],  # C40
                    'QNYNYYYNYN': [3, 1, 1, 0, diuid, 1, ''],  # C41
                    'QNYNYYYNN':  [3, 1, 1, 0, fiuid, 1, ''],  # C42
                    'QNYNYYN':    [3, 1, 1, 0, fiuid, 1, ''],  # C43
                    'QNYNYN':     [3, 1, 1, 1, '',    0, m7],  # C44
                }
                targ = [v for k, v in matrix.items() if tprem.startswith(k)]
                if not targ:
                    targ = [[1, 1, 1, 1, '', 0, 'Key not found: %s' % tprem], ]
                targ = targ[0]
                atitle = analysis.Title() if analysis else "None"
                mtitle = method.Title() if method else "None"
                instdi = {}
                if refan and instrs:
                    instdi = {i.UID(): i.Title() for i in instrs}
                elif not refan and v_instrobjs:
                    instdi = {i.UID(): i.Title() for i in v_instrobjs}
                targ += [instdi, mtitle, atitle, tprem]
                constraints[auid][muid] = targ
                cached_servs[cachedkey][suid][muid] = targ

        return json.dumps(constraints)
