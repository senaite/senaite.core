from Products.Archetypes.config import REFERENCE_CATALOG
from Products.PythonScripts.standard import html_quote
from Products.CMFCore.utils import getToolByName
import plone, json, sys, math, urllib
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
import App

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

        mapping = {}

        # values to be returned to form for this UID
        Result = {'uid': uid}
        try:
            Result['result'] = float(form_result)
        except:
            if 0 in (form_result.find("<"), form_result.find(">")):
                # results with <5 or >10 formats
                self.alerts.append({'uid': uid,
                                    'field': 'Result',
                                    'icon': 'exclamation',
                                    'msg': _('Not a Number')})
                Result['result'] = form_result
                # Don't try calculate this result
                calculation = False
            elif form_result == "":
                # empty result returns "" value to set form result empty
                Result['result'] = form_result
            else:
                # other un-floatable results get forced to 0.
                Result['result'] = 0.0

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
                    # All interims must be float, or error alert is returned
                    try:
                        i['value'] = float(i['value'])
                    except:
                        # interim results with <5 or >10 formats
                        # we only alert if this is the 'current' form field,
                        # so the alert disappears again.
                        if uid == i_uid and self.field == i['keyword']:
                            self.alerts.append({'uid': i_uid,
                                                'field': i['keyword'],
                                                'icon': 'exclamation',
                                                'msg': _('Not a Number')})
                    # all interims are ServiceKeyword.InterimKeyword
                    if i_uid in deps:
                        key = "%s.%s"%(deps[i_uid].getService().getKeyword(),
                                       i['keyword'])
                        mapping[key] = i['value']
                    # this analysis' interims get extra reference
                    # without service keyword prefix
                    if uid == i_uid:
                        mapping[i['keyword']] = i['value']

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

                Result['result'] = result

                self.current_results[uid] = result

            except TypeError:
                # non-numeric arguments in interim mapping?
                Result['result'] = ''
            except ZeroDivisionError, e:
                return None
            except KeyError, e:
                self.alerts.append(
                    {'uid': uid,
                     'field': 'Result',
                     'icon': 'exclamation',
                     'msg': "Key Error: " + html_quote(str(e.args[0]))
                     })
                return None

        try:
            # format calculation result to service precision
            Result['formatted_result'] = precision and Result['result'] and \
                str("%%.%sf" % precision) % Result['result'] or Result['result']
        except:
            # non-float
            Result['formatted_result'] = Result['result']

        # calculate Dry Matter result
        # if parent is not an AR, it's never going to be calculable
        dm = hasattr(analysis.aq_parent, 'getReportDryMatter') and \
            analysis.aq_parent.getReportDryMatter() and \
            analysis.getService().getReportDryMatter()
        if dm:
            dry_service = self.context.bika_setup.getDryMatterService()
            # get the UID of the DryMatter Analysis from our parent AR
            dry_analysis = [a for a in \
                            analysis.aq_parent.getAnalyses(full_objects=True) \
                            if a.getService().UID() == dry_service.UID()]
            if dry_analysis:
                dry_analysis = dry_analysis[0]
                dry_uid = dry_analysis.UID()
                # get the current DryMatter analysis result from the form
                if dry_uid in self.current_results:
                    try:
                        dry_result = float(self.current_results[dry_uid])
                    except:
                        dm = False
                else:
                    try:
                        dry_result = float(dry_analysis.getResult())
                    except:
                        dm = False
            else:
                dm = False
        Result['dry_result'] = dm and dry_result and \
            '%.2f' % ((Result['result'] / dry_result) * 100) or ''

        self.results.append(Result)
        if App.config.getConfiguration().debug_mode:
            logger.info("calc.py: %s->%s %s" % (analysis.aq_parent.id,
                                                analysis.id,
                                                Result))

        self.uncertainties.append({'uid': uid,
                                   'uncertainty':analysis.getUncertainty(
                                       Result['result'])})

        # alert if the result is not in spec
        # for a normal analysis I check against results specificitions
        # for a reference analysis I check the analysis' ReferenceResults
        if analysis.portal_type == 'ReferenceAnalysis':
            in_range = analysis.result_in_range(Result['result'])
        else:
            in_range = analysis.result_in_range(Result['result'], self.spec)
        if in_range[0] == False:
            range_str = _("min:") + str(in_range[1]['min']) + ", " + \
                        _("max:") + str(in_range[1]['max'])
            self.alerts.append({'uid': uid,
                                'field': 'Result',
                                'icon': 'exclamation',
                                'msg': _("Result out of range") + \
                                       " (%s)"%range_str})
        # shoulder
        if in_range[0] == '1':
            range_str = _("min:") + str(in_range[1]['min']) + ", " + \
                        _("max:") + str(in_range[1]['max']) + ", " + \
                        _("error:") + str(in_range[1]['error'])+"%"
            self.alerts.append({'uid': uid,
                                'field': 'Result',
                                'icon': 'warning',
                                'msg': _("Result out of range") + \
                                       " (%s)"%range_str})

        # maybe a service who depends on us must be recalculated.
        if analysis.portal_type == 'ReferenceAnalysis':
            dependents = []
        else:
            dependents = analysis.getDependents()
        if dependents and not Result['result'] == form_result:
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
