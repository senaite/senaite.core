# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
import math

import plone
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote
from bika.lims import bikaMessageFactory as _, api
from bika.lims.api.analysis import is_out_of_range
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IFieldIcons
from bika.lims.utils import t, isnumber
from bika.lims.utils.analysis import format_numeric_result
from zope.component import getAdapters


class ajaxCalculateAnalysisEntry(BrowserView):
    """This view is called by javascript when an analysis' result or interim
       field value is entered.
       Returns a JSON dictionary, or None if no action is required or possible.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def calculate(self, uid=None):
        analysis = self.analyses[uid]
        form_result = self.current_results[uid]['result']
        calculation = analysis.getCalculation()
        if analysis.portal_type == 'ReferenceAnalysis':
            deps = {}
        else:
            deps = {}
            for dep in analysis.getDependencies():
                deps[dep.UID()] = dep
        path = '++resource++bika.lims.images'
        mapping = {}

        # values to be returned to form for this UID
        Result = {'uid': uid, 'result': form_result}
        try:
            Result['result'] = float(form_result)
        except:
            if form_result == "0/0":
                Result['result'] = ""

        if calculation:
            """We need first to create the map of available parameters
               acording to the interims, analyses and wildcards:

             params = {
                    <as-1-keyword>              : <analysis_result>,
                    <as-1-keyword>.<wildcard-1> : <wildcard_1_value>,
                    <as-1-keyword>.<wildcard-2> : <wildcard_2_value>,
                    <interim-1>                 : <interim_result>,
                    ...
                    }
            """

            # Get dependent analyses results and wildcard values to the
            # mapping. If dependent analysis without result found,
            # break and abort calculation
            unsatisfied = False
            for dependency_uid, dependency in deps.items():
                if dependency_uid in self.ignore_uids:
                    unsatisfied = True
                    break

                # LIMS-1769. Allow to use LDL and UDL in calculations.
                # https://jira.bikalabs.com/browse/LIMS-1769
                analysisvalues = {}
                if dependency_uid in self.current_results:
                    analysisvalues = self.current_results[dependency_uid]
                else:
                    # Retrieve the result and DLs from the analysis
                    analysisvalues = {
                        'keyword': dependency.getKeyword(),
                        'result': dependency.getResult(),
                        'ldl': dependency.getLowerDetectionLimit(),
                        'udl': dependency.getUpperDetectionLimit(),
                        'belowldl': dependency.isBelowLowerDetectionLimit(),
                        'aboveudl': dependency.isAboveUpperDetectionLimit(),
                    }
                if analysisvalues['result'] == '':
                    unsatisfied = True
                    break
                key = analysisvalues.get('keyword', dependency.getKeyword())

                # Analysis result
                # All result mappings must be float, or they are ignored.
                try:
                    mapping[key] = float(analysisvalues.get('result'))
                    mapping['%s.%s' % (key, 'RESULT')] = float(analysisvalues.get('result'))
                    mapping['%s.%s' % (key, 'LDL')] = float(analysisvalues.get('ldl'))
                    mapping['%s.%s' % (key, 'UDL')] = float(analysisvalues.get('udl'))
                    mapping['%s.%s' % (key, 'BELOWLDL')] = int(analysisvalues.get('belowldl'))
                    mapping['%s.%s' % (key, 'ABOVEUDL')] = int(analysisvalues.get('aboveudl'))
                except:
                    # If not floatable, then abort!
                    unsatisfied = True
                    break

            if unsatisfied:
                # unsatisfied means that one or more result on which we depend
                # is blank or unavailable, so we set blank result and abort.
                self.results.append({'uid': uid,
                                     'result': '',
                                     'formatted_result': ''})
                return None

            # Add all interims to mapping
            for i_uid, i_data in self.item_data.items():
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
                        pass

                    # all interims are ServiceKeyword.InterimKeyword
                    if i_uid in deps:
                        key = "%s.%s" % (deps[i_uid].getKeyword(),
                                         i['keyword'])
                        mapping[key] = i['value']
                    # this analysis' interims get extra reference
                    # without service keyword prefix
                    if uid == i_uid:
                        mapping[i['keyword']] = i['value']

            # Grab values for hidden InterimFields for only for current calculation
            # we can't allow non-floats through here till we change the eval's
            # interpolation
            hidden_fields = []
            c_fields = calculation.getInterimFields()
            s_fields = analysis.getInterimFields()
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
            formula = calculation.getMinifiedFormula()
            formula = formula.replace('[', '%(').replace(']', ')f')
            try:
                formula = eval("'%s'%%mapping" % formula,
                               {"__builtins__": None,
                                'math': math,
                                'context': self.context},
                               {'mapping': mapping})
                # calculate
                result = eval(formula, calculation._getGlobals())
                Result['result'] = result
                self.current_results[uid]['result'] = result
            except TypeError as e:
                # non-numeric arguments in interim mapping?
                alert = {'field': 'Result',
                         'icon': path + '/exclamation.png',
                         'msg': "{0}: {1} ({2}) ".format(
                             t(_("Type Error")),
                             html_quote(str(e.args[0])),
                             formula)}
                if uid in self.alerts:
                    self.alerts[uid].append(alert)
                else:
                    self.alerts[uid] = [alert, ]
            except ZeroDivisionError as e:
                Result['result'] = '0/0'
                Result['formatted_result'] = '0/0'
                self.current_results[uid]['result'] = '0/0'
                self.results.append(Result)
                alert = {'field': 'Result',
                         'icon': path + '/exclamation.png',
                         'msg': "{0}: {1} ({2}) ".format(
                             t(_("Division by zero")),
                             html_quote(str(e.args[0])),
                             formula)}
                if uid in self.alerts:
                    self.alerts[uid].append(alert)
                else:
                    self.alerts[uid] = [alert, ]
                return None
            except KeyError as e:
                alert = {'field': 'Result',
                         'icon': path + '/exclamation.png',
                         'msg': "{0}: {1} ({2}) ".format(
                             t(_("Key Error")),
                             html_quote(str(e.args[0])),
                             formula)}
                if uid in self.alerts:
                    self.alerts[uid].append(alert)
                else:
                    self.alerts[uid] = [alert, ]

        # format result
        try:
            Result['formatted_result'] = format_numeric_result(analysis,
                                                               Result['result'])
        except ValueError:
            # non-float
            Result['formatted_result'] = Result['result']

        self.results.append(Result)

        # if App.config.getConfiguration().debug_mode:
        #     logger.info("calc.py: %s->%s %s" % (analysis.aq_parent.id,
        #                                         analysis.id,
        #                                         Result))

        # LIMS-1808 Uncertainty calculation on DL
        # https://jira.bikalabs.com/browse/LIMS-1808
        flres = Result.get('result', None)
        if flres and isnumber(flres):
            flres = float(flres)
            anvals = self.current_results[uid]
            isldl = anvals.get('isldl', False)
            isudl = anvals.get('isudl', False)
            ldl = anvals.get('ldl', 0)
            udl = anvals.get('udl', 0)
            ldl = float(ldl) if isnumber(ldl) else 0
            udl = float(udl) if isnumber(udl) else 10000000
            belowldl = (isldl or flres < ldl)
            aboveudl = (isudl or flres > udl)
            unc = '' if (belowldl or aboveudl) else analysis.getUncertainty(Result.get('result'))
            if not (belowldl or aboveudl):
                self.uncertainties.append({'uid': uid, 'uncertainty': unc})

        # maybe a service who depends on us must be recalculated.
        if analysis.portal_type == 'ReferenceAnalysis':
            dependents = []
        else:
            dependents = analysis.getDependents()
        if dependents:
            for dependent in dependents:
                dependent_uid = dependent.UID()
                # ignore analyses that no longer exist.
                if dependent_uid in self.ignore_uids or \
                   dependent_uid not in self.analyses:
                    continue
                self.calculate(dependent_uid)

        # Render out of range / in shoulder alert info
        self._render_range_alert(analysis, Result["result"])

    def _render_range_alert(self, analysis, result):
        """Appends an entry for the passed in analysis in self.alerts if the
        passed in tentative result is out of range or in shoulder range, in
        accordance with the assigned results range for the passed in analysis

        :param analysis: analysis object to be evaluated
        :param result: the tentative result to test if out of range/in shoulder
        """
        if not analysis or not api.is_floatable(result):
            return
        out_of_range, out_of_shoulder = is_out_of_range(analysis, result)
        if not out_of_range:
            return

        result_range = analysis.getResultsRange()
        rngstr = "{0} {1}, {2} {3}".format(
            t(_("min")), result_range.get("min"),
            t(_("max")), result_range.get("max"))
        message = "Result out of range"
        icon = "exclamation.png"
        if not out_of_shoulder:
            message = "Result in shoulder range"
            icon = "warning.png"

        uid = api.get_uid(analysis)
        alert = self.alerts.get(uid, [])
        alert.append({'icon': "++resource++bika.lims.images/{}".format(icon),
                      'msg': "{0} ({1})".format(t(_(message)), rngstr),
                      'field': "Result"})
        self.alerts[uid] = alert

    def __call__(self):
        self.rc = getToolByName(self.context, REFERENCE_CATALOG)
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)

        self.spec = self.request.get('specification', None)

        # information about the triggering element
        uid = self.request.get('uid')
        self.field = self.request.get('field')
        self.value = self.request.get('value')

        self.current_results = json.loads(self.request.get('results'))
        form_results = json.loads(self.request.get('results'))
        self.item_data = json.loads(self.request.get('item_data'))

        # these get sent back the the javascript
        self.alerts = {}
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


class ajaxGetMethodCalculation(BrowserView):
    """ Returns the calculation assigned to the defined method.
        uid: unique identifier of the method
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        calcdict = {}
        uc = getToolByName(self, 'uid_catalog')
        method = uc(UID=self.request.get("uid", '0'))
        if method and len(method) == 1:
            calc = method[0].getObject().getCalculation()
            if calc:
                calcdict = {'uid': calc.UID(),
                            'title': calc.Title()}
        return json.dumps(calcdict)


class ajaxGetAvailableCalculations(BrowserView):
    """
    Returns all available calculations.
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)

        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [(i.UID, i.Title)
                 for i in bsc(portal_type='Calculation',
                              inactive_state='active')]
        items.sort(lambda x, y: cmp(x[1], y[1]))
        items.insert(0, ('', _("None")))
        calcdict = [{'uid': calc[0], 'title': calc[1]} for calc in items]

        return json.dumps(calcdict)
