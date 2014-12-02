from bika.lims.browser import BrowserView
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IFieldIcons
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims import logger
from bika.lims.utils import to_utf8
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote
from bika.lims.utils.analysis import format_numeric_result
from zope.component import adapts
from zope.component import getAdapters
from zope.interface import implements

import json
import math
import plone


class CalculationResultAlerts(object):

    """This uses IAnalysis.ResultOutOfRange on values in request.
    To validate results at ajax calculation time, make more adapters like this
    one, from IFieldIcons.  Any existing IAnalysis/IFieldIcon adapters
    (AnalysisOutOfRange) have already been called.
    """

    adapts(IAnalysis)
    implements(IFieldIcons)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, specification=None, **kwargs):
        workflow = getToolByName(self.context, 'portal_workflow')
        astate = workflow.getInfoFor(self.context, 'review_state')
        if astate == 'retracted':
            return {}
        result = self.context.getResult() if result is None else result
        alerts = {}
        path = '++resource++bika.lims.images'
        uid = self.context.UID()
        try:
            indet = result.startswith("<") or result.startswith(">")
        except AttributeError:
            indet = False
        if indet:
            alert = {'field': 'Result',
                     'icon': path + '/exclamation.png',
                     'msg': t(_("Indeterminate result"))}
            if uid in alerts:
                alerts[uid].append(alert)
            else:
                alerts[uid] = [alert, ]
        return alerts


class ajaxCalculateAnalysisEntry(BrowserView):

    """ This view is called by javascript when an analysis' result or interim
        field value is entered. Returns a JSON dictionary, or None if no
        action is required or possible.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def calculate(self, uid=None):
        analysis = self.analyses[uid]
        form_result = self.current_results[uid]
        service = analysis.getService()
        calculation = service.getCalculation()
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
                    pass
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
                        key = "%s.%s" % (deps[i_uid].getService().getKeyword(),
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
            formula = calculation.getMinifiedFormula()
            formula = formula.replace('[', '%(').replace(']', ')f')
            try:
                formula = eval("'%s'%%mapping" % formula,
                               {"__builtins__": None,
                                'math': math,
                                'context': self.context},
                               {'mapping': mapping})
                # calculate
                result = eval(formula)
                Result['result'] = result
                self.current_results[uid] = result
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
                self.current_results[uid] = '0/0'
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
        belowmin = False
        abovemax = False
        # Some analyses will not have AnalysisSpecs, eg, ReferenceAnalysis
        if hasattr(analysis, 'getAnalysisSpecs'):
            specs = analysis.getAnalysisSpecs()
            specs = specs.getResultsRangeDict() if specs is not None else {}
            specs = specs.get(analysis.getKeyword(), {})
            hidemin = specs.get('hidemin', '')
            hidemax = specs.get('hidemax', '')
            if Result.get('result', ''):
                fresult = Result['result']
                try:
                    belowmin = hidemin and fresult < float(hidemin) or False
                except ValueError:
                    belowmin = False
                    pass
                try:
                    abovemax = hidemax and fresult > float(hidemax) or False
                except ValueError:
                    abovemax = False
                    pass
        if belowmin is True:
            Result['formatted_result'] = '< %s' % hidemin
        elif abovemax is True:
            Result['formatted_result'] = '> %s' % hidemax
        else:
            try:
                Result['formatted_result'] = format_numeric_result(analysis,
                                                                   Result['result'])
            except ValueError:
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

        # if App.config.getConfiguration().debug_mode:
        #     logger.info("calc.py: %s->%s %s" % (analysis.aq_parent.id,
        #                                         analysis.id,
        #                                         Result))

        self.uncertainties.append({'uid': uid,
                                   'uncertainty': analysis.getUncertainty(
                                       Result['result'])})

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

        # These self.alerts are just for the json return.
        # we're placing the entire form's results in kwargs.
        adapters = getAdapters((analysis, ), IFieldIcons)
        for name, adapter in adapters:
            alerts = adapter(result=Result['result'], form_results=self.current_results)
            if alerts:
                if analysis.UID() in self.alerts:
                    self.alerts[analysis.UID()].extend(alerts[analysis.UID()])
                else:
                    self.alerts[analysis.UID()] = alerts[analysis.UID()]

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
