from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote
from zope.i18n import translate

import App
import json
import math
import plone
import sys
import urllib


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
            if form_result.startswith("<") or \
               form_result.startswith(">"):
                # Indeterminate results
                Indet = translate(_("Indeterminate result"))
                self.alerts.append({'uid': uid,
                                    'field': 'Result',
                                    'icon': 'exclamation',
                                    'msg': Indet})
                Result['result'] = form_result
                # Don't try calculate this result
                calculation = False
            elif form_result == "":
                # empty result returns "" value to set form result empty
                Result['result'] = form_result
            elif form_result == "0/0":
                # 0/0 result means divbyzero: set result value to empty
                Result['result'] = ""
            # else:
            #     # other un-floatable results get forced to 0.
            #     Result['result'] = 0.0

        # This gets set if <> is detected in interim values, so that
        # TypeErrors during calculation can set the correct alert message
        indeterminate = False

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
                # All mappings must be float, or they are ignored.
                try:
                    mapping[key] = float(self.current_results[dependency_uid])
                except:
                    continue
                    # # indeterminate interim values (<x, >x, invalid)
                    # # set 'indeterminate' flag on this analyses' result
                    # indeterminate = True
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
                    # All interims must be float, or they are ignored.
                    try:
                        i['value'] = float(i['value'])
                    except:
                        continue
                        # # indeterminate interim values (<x, >x, invald)
                        # # set 'indeterminate' flag on this analyses' result
                        # indeterminate = True

                    # all interims are ServiceKeyword.InterimKeyword
                    if i_uid in deps:
                        key = "%s.%s"%(deps[i_uid].getService().getKeyword(),
                                       i['keyword'])
                        mapping[key] = i['value']
                    # this analysis' interims get extra reference
                    # without service keyword prefix
                    if uid == i_uid:
                        mapping[i['keyword']] = i['value']

            # Grab values for hidden InterimFields for only for current calculation
            # we can't allow non-floats through here till we change the eval's interpolation
            hidden_fields = []
            c_fields = calculation.getInterimFields()
            s_fields = service.getInterimFields()
            for field in c_fields:
                if field.get('hidden', False):
                    hidden_fields.append(field['keyword'])
                    try:
                        mapping[field['keyword']] = float(field['value'])
                    except ValueError:
                        pass
            # also grab stickier defaults from AnalysisService
            for field in s_fields:
                if field['keyword'] in hidden_fields:
                    try:
                        mapping[field['keyword']] = float(field['value'])
                    except ValueError:
                        pass

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
                if indeterminate:
                    indet = self.context.translate(_('Indet'))
                    Indet = self.context.translate(_("Indeterminate result"))
                    Result['result'] = indet
                    self.alerts.append({'uid': uid,
                                        'field': 'Result',
                                        'icon': 'exclamation',
                                        'msg': Indet})
                # Non-floatable results are not actually invalid
                # else:
                #     inval = self.context.translate(_("Invalid result"))
                #     self.alerts.append({'uid': uid,
                #                         'field': 'Result',
                #                         'icon': 'exclamation',
                #                         'msg': inval})

            except ZeroDivisionError, e:
                Result['result'] = '0/0'
                Result['formatted_result'] = '0/0'
                self.current_results[uid] = '0/0'
                self.alerts.append(
                    {'uid': uid,
                    'field': 'Result',
                    'icon': 'exclamation',
                    'msg': "Division by zero: " + html_quote(str(e.args[0])) + "("+formula+")"
                    })
                self.results.append(Result)
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
            dry_analysis = [a for a in
                            analysis.aq_parent.getAnalyses(full_objects=True)
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
            range_str = _("min") + " " + str(in_range[1]['min']) + ", " + \
                        _("max") + " " + str(in_range[1]['max'])
            self.alerts.append({'uid': uid,
                                'field': 'Result',
                                'icon': 'exclamation',
                                'msg': _("Result out of range") + \
                                       " (%s)"%range_str})
        # shoulder
        if in_range[0] == '1':
            range_str = _("min") + " " + str(in_range[1]['min']) + ", " + \
                        _("max") + " " + str(in_range[1]['max']) + ", " + \
                        _("error") + " " + str(in_range[1]['error'])+"%"
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


class ajaxGetInterimFields:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        uc = getToolByName(self.context, 'uid_catalog')
        calc = self.request['calc']
        calcs = uc(UID=calc)
        if calcs:
            calc = calcs[0].getObject()
        else:
            return json.dumps([])

        return json.dumps(calc.getInterimFields())
