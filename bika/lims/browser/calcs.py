from Products.CMFCore.utils import getToolByName
import plone, json, sys, math, urllib
from bika.lims import bikaMessageFactory as _
from bika.lims import logger

class ajaxCalculateAnalysisEntry():
    """ This view is called by javascript when an analysis' result or interim field value is
        entered. Returns a JSON dictionary, or None if no action is required or possible.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def calculate(self, uid = None):

        recursing = uid and True or False
        uid = uid or self.uid
        if uid in self.calculated: return None
        self.calculated.append(uid)

        analysis = self.analyses[uid]
        form_result = self.form_results[uid]
        service = self.services[self.UIDtoUID[uid]]
        precision = service.getPrecision()
        calculation = service.getCalculation()
        if not self.dependencies.has_key(uid):
            self.dependencies[uid] = calculation and \
                calculation.getDependentServices() or []

        result = None
        mapping = {}

        # If we have no dependencies, why recurse into us?
        if recursing and not self.dependencies[uid]:
            return None

        # check if all dependent services have values in the form_results,
        # and add them to mapping
        unsatisfied = False
        for dep in self.dependencies[uid]:
            dep_uid = dep.UID()
            for a in self.analyses:
                if self.UIDtoUID[dep_uid] == a:
                    if self.form_results[self.UIDtoUID[dep_uid]] == "":
                        unsatisfied = True
                        break
                    try:
                        mapping[dep.getKeyword()] = float(
                            self.form_results[self.UIDtoUID[dep_uid]])
                    except:
                        mapping[dep.getKeyword()] = \
                               self.form_results[self.UIDtoUID[dep_uid]]
                    break
        # reset form result and fail, if any dependencies are unsatisfied
        if unsatisfied:
            self.results.append({'uid': uid,
                                 'result': '',
                                 'formatted_result': ''})
            return None

        if calculation:

            # check if all interim fields in this row have values in the form
            # data add field value to the mapping, amd set self.item_data
            new_item_data = []
            for i in self.item_data[uid]:

                # If an interim field is blank, remove the row
                # result from form values
                if self.value == '':
                    self.form_results[uid] = ''
                    self.results.append({'uid': uid,
                                         'result': '',
                                         'formatted_result': ''})

                # Set the new value if it's changed
                if i['keyword'] == self.field:
                    i['value'] = self.value

                new_item_data.append(i)
                mapping[i['keyword']] = i['value']

            self.item_data[uid] = new_item_data

            type_error = False
            for key, value in mapping.items():
                try:
                    mapping[key] = float(value)
                except Exception, e:
                    type_error = True
            if type_error:
                return None

            formula = calculation.getFormula()
            formula = formula.replace('[', '%(').replace(']', ')f')

            try:
                # mapping values are keyed by ServiceKeyword or InterimField keyword
                formula = eval("'%s'%%mapping" % formula,
                               {"__builtins__":None, 'math':math},
                               {'mapping': mapping})
                # calculate
                result = eval(formula)
                # always format calculation result to service precision
                result = precision and str("%%.%sf" % precision) % result or \
                       result

                self.results.append({'uid': uid, 'result': result, 'formatted_result': result})
                self.form_results[uid] = result
            except ZeroDivisionError, e:
                return None
            except KeyError, e:
                self.alerts.append({'uid': uid, 'field': 'Result', 'icon': 'exclamation', 'msg': "Key Error: " + str(e.args[0])})
                return None
            except Exception, e:
                self.alerts.append({'uid': uid, 'field': 'Result', 'icon': 'exclamation', 'msg': "Exception: " + str(e.args[0])})
                return None

        else:
            # if nothing's changed, set form to show the original value
            self.results.append({'uid': uid, 'result': form_result, 'formatted_result': form_result})

        # Uncertainty value for this result
        self.uncertainties.append({'uid': uid,
                                   'uncertainty':analysis.getUncertainty(result and result or form_result)})

        # alert if the result is not in spec
        # for a normal analysis this checks against lab/client results specificitions
        # for a reference analysis this checks against the analysis' ReferenceResults
        if analysis.portal_type == 'ReferenceAnalysis':
            in_range = analysis.result_in_range(result and result or form_result)
        else:
            in_range = analysis.result_in_range(result and result or form_result, self.specification)
        if in_range == True: pass
        if in_range == False:
            self.alerts.append({'uid': uid, 'field': 'Result', 'icon': 'exclamation', 'msg': _("Result out of range")})
        if in_range == '1':
            self.alerts.append({'uid': uid, 'field': 'Result', 'icon': 'warning', 'msg': _("Result out of range")}) # : shoulder

        # maybe a service who depends on us must be recalculated.
        if result != form_result:
            for recurse_uid, recurse_val in self.form_results.items():
                # if it's in recurse_uids its my ancestor.
                if recurse_uid in self.recurse_uids:
                    continue
                # ignore analyses that no longer exist.
                if recurse_uid in self.ignore_uids:
                    continue
                # recalculate it
                self.recurse_uids.append(recurse_uid)
                self.calculate(recurse_uid)
                self.recurse_uids.remove(recurse_uid)

    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)

        # uid of submitted analysis
        self.uid = self.request.get('uid')
        # field last edited
        self.field = self.request.get('field')
        self.value = self.request.get('value')
        self.specification = self.request.get('specification', 'lab')
        self.form_results = json.loads(self.request.get('results'))
        self.pristine_form_results = self.form_results

        # these are sent back to the js
        try: self.item_data = json.loads(self.request.get('item_data', ''))
        except: self.item_data = []
        self.uncertainties = []
        self.alerts = []
        self.results = []
        self.ignore_uids = []

        self.services = {}
        self.analyses = {}
        self.dependencies = {}
        # once a result is calculated for an analysis, recurse it not again
        self.calculated = []
        # Contains all Service UIDs as keys with the Analysis UID as the value
        # Also contains all Analysis UIDS as keys, with their Service UIDs as values.
        self.UIDtoUID = {}
        for analysis_uid, result in self.form_results.items():
            analysis = rc.lookupObject(analysis_uid)
            if not analysis:
                # ignore analysis if object no longer exists
                self.ignore_uids.append(analysis_uid)
                continue
            service = analysis.getService()
            service_uid = service.UID()
            self.analyses[analysis_uid] = analysis
            self.services[service_uid] = service
            self.UIDtoUID[service_uid] = analysis_uid
            self.UIDtoUID[analysis_uid] = service_uid

        if self.uid not in self.ignore_uids:
            self.recurse_uids = [self.uid, ]
            self.calculate()

        return json.dumps({'item_data': self.item_data,
                           'alerts': self.alerts,
                           'uncertainties': self.uncertainties,
                           'results': self.results})
