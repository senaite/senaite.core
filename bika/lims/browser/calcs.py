from Products.Archetypes.config import REFERENCE_CATALOG
from Products.PythonScripts.standard import html_quote
from Products.CMFCore.utils import getToolByName
import plone, json, sys, math, urllib
from bika.lims import bikaMessageFactory as _
from bika.lims import logger

class ajaxCalculateAnalysisEntry():
    """ This view is called by javascript when an analysis' result or interim
        field value is entered. Returns a JSON dictionary, or None if no
        action is required or possible.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def calculate(self, uid = None):

        analysis = self.analyses[uid]
        form_result = self.current_results[uid]
        service = analysis.getService()
        precision = service.getPrecision()
        calculation = service.getCalculation()
        if analysis.portal_type == 'ReferenceAnalysis':
            deps = {}
        else:
            deps = {}
            for dep in analysis.getDependencies():
                deps[dep.UID()] = dep

        result = None
        mapping = {}

        if calculation:
            # add all our dependent analyses results to the mapping.
            # Retrieve value from database if it's not in the current_results.
            unsatisfied = False
            for dependency_uid, dependency in deps.items():
                if dependency_uid in self.ignore_uids:
                    unsatisfied = True
                    break
                if dependency_uid in self.current_results:
                    result = self.current_results[dependency_uid]
                else:
                    result = dependency.getResult()
                if result == '':
                    unsatisfied = True
                    break
                key = dependency.getService().getKeyword()
                mapping[key] = self.current_results[dependency_uid]
            if unsatisfied:
                # unsatisfied means that one or more result on which we depend
                # is blank or unavailable, so we set blank result and abort.
                self.results.append({'uid': uid,
                                     'result': '',
                                     'formatted_result': ''})
                return None

            # Add all interims to mapping
            for i_uid,i_data in self.item_data.items():
                for i in i_data:
                    # if this interim belongs to current analysis and is blank,
                    # return an empty result for this analysis.
                    if i_uid == uid and i['value'] == '':
                        self.results.append({'uid': uid,
                                             'result': '',
                                             'formatted_result': ''})
                        return None
                    # all interims are ServiceKeyword.InterimKeyword
                    if i_uid in deps:
                        key = "%s.%s"%(deps[i_uid].getKeyword(), i['keyword'])
                        mapping[key] = i['value']
                    # this analysis' interims get extra reference
                    # without service keyword prefix
                    if uid == i_uid:
                        mapping[i['keyword']] = i['value']

            # coerce everything to float
            for key, value in mapping.items():
                mapping[key] = float(value)

            # convert formula to a valid python string, ready for interpolation
            formula = calculation.getFormula()
            formula = formula.replace('[', '%(').replace(']', ')f')

            try:
                formula = eval("'%s'%%mapping" % formula,
                               {"__builtins__":None,
                                'math':math,
                                'context':self.context},
                               {'mapping': mapping})
                # calculate
                result = eval(formula)
                # format calculation result to service precision
                formatted_result = precision and \
                    str("%%.%sf" % precision) % result or result

                self.results.append({'uid': uid,
                                     'result': result,
                                     'formatted_result': formatted_result})
                self.current_results[uid] = result
            except ZeroDivisionError, e:
                return None
            except KeyError, e:
                self.alerts.append({'uid': uid,
                                    'field': 'Result',
                                    'icon': 'exclamation',
                                    'msg': "Key Error: " + html_quote(str(e.args[0]))})
                return None

        self.uncertainties.append({'uid': uid,
                                   'uncertainty':analysis.getUncertainty(
                                       result and result or form_result)})

        # alert if the result is not in spec
        # for a normal analysis I check against results specificitions
        # for a reference analysis I check the analysis' ReferenceResults
        if analysis.portal_type == 'ReferenceAnalysis':
            in_range = analysis.result_in_range(result and result or form_result)
        else:
            in_range = analysis.result_in_range(result and result or form_result, self.spec)
        if in_range[0] == False:
            range_str = _("min:") + str(in_range[1]['min']) + ", " + \
                        _("max:") + str(in_range[1]['max'])
            self.alerts.append({'uid': uid,
                                'field': 'Result',
                                'icon': 'exclamation',
                                'msg': _("Result out of range" + " (%s)"%range_str)})
        # shoulder
        if in_range[0] == '1':
            range_str = _("min:") + str(in_range[1]['min']) + ", " + \
                        _("max:") + str(in_range[1]['max']) + ", " + \
                        _("error:") + str(in_range[1]['error'])+"%"
            self.alerts.append({'uid': uid,
                                'field': 'Result',
                                'icon': 'warning',
                                'msg': _("Result out of range") + " (%s)"%range_str})

        # maybe a service who depends on us must be recalculated.
        if analysis.portal_type == 'ReferenceAnalysis':
            dependents = []
        else:
            dependents = analysis.getDependents()
        if dependents and not result == form_result:
            for dependent in dependents:
                dependent_uid = dependent.UID()
                # ignore analyses that no longer exist.
                if dependent_uid in self.ignore_uids or \
                   dependent_uid not in self.analyses:
                    continue
                self.calculate(dependent_uid)

    def __call__(self):
        self.rc = getToolByName(self.context, REFERENCE_CATALOG)
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)

        self.spec = self.request.get('specification', 'lab')

        # information about the triggering element
        uid = self.request.get('uid')
        self.field = self.request.get('field')
        self.value = self.request.get('value')

        self.current_results = json.loads(self.request.get('results'))
        form_results = json.loads(self.request.get('results'))
        self.item_data = json.loads(self.request.get('item_data'))

        # these get sent back the the javascript
        self.alerts = []
        self.uncertainties = []
        self.results = []

        self.services = {}
        self.analyses = {}
        # ignore these analyses if objects no longer exist
        self.ignore_uids = []

        for analysis_uid, result in self.current_results.items():
            analysis = self.rc.lookupObject(analysis_uid)
            if not analysis:
                self.ignore_uids.append(analysis_uid)
                continue
            self.analyses[analysis_uid] = analysis

        if uid not in self.ignore_uids:
            self.calculate(uid)

        results = []
        for result in self.results:
            if result['uid'] in form_results.keys() and \
               result['result'] != form_results[result['uid']]:
                results.append(result)

        return json.dumps({'alerts': self.alerts,
                           'uncertainties': self.uncertainties,
                           'results': results})
