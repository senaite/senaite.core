from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from decimal import Decimal
import json

class AnalysisRequestViewView(BrowserView):
    """ AR View form
    """
    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")

    def __call__(self):
        return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def now(self):
        return DateTime()

    def Categories(self):
        """ Dictionary keys: field/lab
            Dictionary values: (Category Title,category UID)
            This returns only cats which have analyses selected in the current AR
        """
        pc = getToolByName(self.context, 'portal_catalog')
        cats = {}
        for analysis in pc(portal_type = "Analysis", getRequestID = self.context.id):
            analysis = analysis.getObject()
            service = analysis.getService()
            poc = service.getPointOfCapture()
            if not cats.has_key(poc): cats[poc] = []
            cat = (service.getCategoryName(), service.getCategoryUID())
            if cat not in cats[poc]: cats[poc].append(cat)
        return cats

    def result_in_range(self, analysis, sampletype_uid, specification):
        ## Script (Python) "result_in_range"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=analysis, sampletype_uid, specification
        ##title=Check if result in range
        ##
        from decimal import Decimal
        result_class = ''
        result = analysis.getResult()
        try:
            result = Decimal(result)
        except:
            # if it is not an integer result we assume it is in range
            return ''

        service = analysis.getService()
        aservice = service.UID()

        if analysis.portal_type in ['Analysis', 'RejectAnalysis']:
            if analysis.portal_type == 'RejectAnalysis':
                client_uid = analysis.getRequest().getClientUID()
            else:
                client_uid = analysis.getClientUID()

            if specification == 'lab':
                a = self.context.portal_catalog(portal_type = 'LabAnalysisSpec',
                                                getSampleTypeUID = sampletype_uid)
            else:
                a = self.context.portal_catalog(portal_type = 'AnalysisSpec',
                                                getSampleTypeUID = sampletype_uid,
                                                getClientUID = client_uid)

            if a:
                spec_obj = a[0].getObject()
                spec = spec_obj.getResultsRangeDict()
            else:
                return ''

            result_class = 'out_of_range'
            if spec.has_key(aservice):
                spec_min = Decimal(spec[aservice]['min'])
                spec_max = Decimal(spec[aservice]['max'])
                if spec_min <= result <= spec_max:
                    result_class = ''
                #else:
                #    """ check if in error range """
                #    error_amount = result * Decimal(spec[aservice]['error']) / 100
                #    error_min = result - error_amount
                #    error_max = result + error_amount
                #    if ((result < spec_min) and (error_max >= spec_min)) or \
                #       ((result > spec_max) and (error_min <= spec_max)):
                #        result_class = 'in_error_range'
            else:
                result_class = ''

        elif analysis.portal_type == 'StandardAnalysis':
            result_class = ''
            specs = analysis.aq_parent.getResultsRangeDict()
            if specs.has_key(aservice):
                spec = specs[aservice]
                if (result < Decimal(spec['min'])) or (result > Decimal(spec['max'])):
                    result_class = 'out_of_range'
            return specs

        elif analysis.portal_type == 'DuplicateAnalysis':
            service = analysis.getService()
            service_id = service.getId()
            service_uid = service.UID()
            wf_tool = self.context.portal_workflow
            if wf_tool.getInfoFor(analysis, 'review_state', '') == 'rejected':
                ws_uid = self.context.UID()
                for orig in self.context.portal_catalog(portal_type = 'RejectAnalysis',
                                                        getWorksheetUID = ws_uid,
                                                        getServiceUID = service_uid):
                    orig_analysis = orig.getObject()
                    if orig_analysis.getRequest().getRequestID() == analysis.getRequest().getRequestID():
                        break
            else:
                ar = analysis.getRequest()
                orig_analysis = ar[service_id]
            orig_result = orig_analysis.getResult()
            try:
                orig_result = float(orig_result)
            except ValueError:
                return ''
            dup_variation = service.getDuplicateVariation()
            dup_variation = dup_variation and dup_variation or 0
            range_min = result - (result * dup_variation / 100)
            range_max = result + (result * dup_variation / 100)
            if range_min <= orig_result <= range_max:
                result_class = ''
            else:
                result_class = 'out_of_range'

        return result_class

    def get_calc_columns(self, batch):
        ##
        ##title=Determine which calculation columns are required
        ##
        vm = False # vessel mass
        sm = False # sample mass
        nm = False # nett mass
        gm = False # nett mass
        tv = False # titration vol
        tf = False # titration factor

        for analysis in batch:
            calc_type = analysis.getCalcType()
            if calc_type == None:
                continue
            if calc_type in ['wl', 'rw']:
                gm = True
                vm = True
                nm = True
            if calc_type in ['wlt', 'rwt']:
                vm = True
                sm = True
                nm = True
            if calc_type in ['t', ]:
                tv = True
                tf = True
        cols = []
        if vm: cols.append('vm')
        if sm: cols.append('sm')
        if gm: cols.append('gm')
        if nm: cols.append('nm')
        if tv: cols.append('tv')
        if tf: cols.append('tf')

        return cols

    def get_requested_analyses(self):
        ##
        ##title=Get requested analyses
        ##
        wf_tool = getToolByName(self.context, 'portal_workflow')
        result = []
        cats = {}
        for analysis in self.context.getAnalyses():
            if wf_tool.getInfoFor(analysis, 'review_state', '') == 'not_requested':
                continue
            if not cats.has_key(analysis.getService().getCategoryName()):
                cats[analysis.getService().getCategoryName()] = {}
            analyses = cats[analysis.getService().getCategoryName()]
            analyses[analysis.Title()] = analysis
            cats[analysis.getService().getCategoryName()] = analyses

        cat_keys = cats.keys()
        cat_keys.sort(lambda x, y:cmp(x.lower(), y.lower()))

        for cat_key in cat_keys:
            analyses = cats[cat_key]
            analysis_keys = analyses.keys()
            analysis_keys.sort(lambda x, y:cmp(x.lower(), y.lower()))
            for analysis_key in analysis_keys:
                result.append(analyses[analysis_key])

        return result

    def get_analyses_not_requested(self):
        ##
        ##title=Get analyses which have not been requested by the client
        ##

        wf_tool = getToolByName(self.context, 'portal_workflow')
        result = []
        for analysis in self.context.getAnalyses():
            if wf_tool.getInfoFor(analysis, 'review_state', '') == 'not_requested':
                result.append(analysis)

        return result

    def get_analysisrequest_verifier(self, analysisrequest):
        ## Script (Python) "get_analysisrequest_verifier"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=analysisrequest
        ##title=Get analysis workflow states
        ##

        ## get the name of the member who last verified this AR
        ##  (better to reverse list and get first!)

        wtool = getToolByName(self.context, 'portal_workflow')
        mtool = getToolByName(self.context, 'portal_membership')

        verifier = None
        try:
            review_history = wtool.getInfoFor(analysisrequest, 'review_history')
        except:
            return 'access denied'

        [review for review in review_history if review.get('action', '')]
        if not review_history:
            return 'no history'
        for items in  review_history:
            action = items.get('action')
            if action != 'verify':
                continue
            actor = items.get('actor')
            member = mtool.getMemberById(actor)
            verifier = member.getProperty('fullname')
            if verifier is None or verifier == '':
                verifier = actor
        return verifier


class AnalysisRequestAddView(BrowserView):
    """ The main AR Add form
    """
    template = ViewPageTemplateFile("templates/analysisrequest_edit.pt")
    col_count = 4
    came_from = "add"

    def __call__(self):
        if self.request.form.has_key("submitted"):
            return analysisrequest_add_submit(self.context, self.request)
        else:
            return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def arprofiles(self):
        """ Return applicable client and Lab ARProfile records
        """
        profiles = []
        pc = getToolByName(self.context, 'portal_catalog')
        for proxy in pc(portal_type = 'ARProfile', getClientUID = self.context.UID(), sort_on = 'sortable_title'):
            profiles.append(proxy.getObject()) #XXX getObject()
        for proxy in pc(portal_type = 'LabARProfile', sort_on = 'sortable_title'):
            profile = proxy.getObject()
            profile.setTitle("Lab: %s" % profile.Title())
            profiles.append(proxy.getObject()) #XXX getObject()
        return profiles

    def Categories(self):
        """ Dictionary keys: field/lab
            Dictionary values: (Category Title,category UID)
        """
        pc = getToolByName(self.context, 'portal_catalog')
        cats = {}
        for service in pc(portal_type = "AnalysisService"):
            poc = service.getPointOfCapture
            if not cats.has_key(poc): cats[poc] = []
            cat = (service.getCategoryName, service.getCategoryUID)
            if cat not in cats[poc]: cats[poc].append(cat)
        return cats

class AnalysisRequestEditView(AnalysisRequestAddView):
    template = ViewPageTemplateFile("templates/analysisrequest_edit.pt")
    col_count = 1
    came_from = "edit"

    def SelectedServices(self):
        """ res is a list of lists.  [[category uid, service uid],...]
            for each service selected
        """
        pc = getToolByName(self.context, 'portal_catalog')
        res = []
        for analysis in pc(portal_type = "Analysis", getRequestID = self.context.RequestID):
            analysis = analysis.getObject() # XXX getObject
            service = analysis.getService()
            res.append([service.getCategoryUID(), service.UID(), service.getPointOfCapture()])
        return res

class AnalysisRequestManageResultsView(AnalysisRequestViewView):
    template = ViewPageTemplateFile("templates/analysisrequest_analyses.pt")

    def __call__(self):

        form = self.request.form

    # import pprint
    # pprint.pprint(form)

        wf_tool = getToolByName(self.context, 'portal_workflow')
        pc = getToolByName(self.context, 'portal_catalog')

        if form.has_key('workflow_action') and form['workflow_action'] and form.has_key('ids'):
            success = {}
            workflow_action = form['workflow_action']
            ids = form['ids']

            for id in ids:
                analysis = pc(path = { "query": [self.context.id], "level" : 3 },
                              id = id)[0].getObject()
                try:
                    wf_tool.doActionFor(analysis, workflow_action)
                    success[id] = workflow_action
                except:
                    # Since we can have mixed statuses on selected analyses it can occur
                    # quite easily that the workflow_action doesn't work for some objects
                    # but we need to keep on going.
                    pass

            # if only some analyses were published we still send an email
            if workflow_action in ['publish', 'republish', 'prepublish'] and \
               self.context.portal_type == 'AnalysisRequest' and \
               len(success.keys()) > 0:
                contact = self.context.getContact()
                analysis_requests = [self.context]
                contact.publish_analysis_requests(self.context, contact, analysis_requests, None)
                # cc contacts
                for cc_contact in self.context.getCCContact():
                    contact.publish_analysis_requests(self.context, cc_contact, analysis_requests, None)
                # cc emails
                cc_emails = self.context.getCCEmails()
                if cc_emails:
                    contact.publish_analysis_requests(self.context, None, analysis_requests, cc_emails)

            transaction_note(str(ids) + ' transitioned ' + workflow_action)

            # It is necessary to set the context to override context from content_status_modify
            portal_message = 'Content has been changed'
            # Determine whether only partial content has been changed
            if self.context.REQUEST.form.has_key('GuardError'):
                guard_error = self.context.REQUEST['GuardError']
                if guard_error == 'Fail':
                    portal_message = 'Content has not been changed'
                elif guard_error == 'Partial':
                    portal_message = 'Some content has been changed'

            self.request.RESPONSE.redirect(self.context.absolute_url() + "/analysisrequest_analyses")

        elif form.has_key("submitted"):

            for key, value in form.items():
                if key.startswith('results'):
                    id = key.split('results.')[-1]
                    analysis = pc(path = { "query": [self.context.id], "level" : 3 },
                                  id = id)[0].getObject()
                    if analysis.getCalcType() == 'dep':
                        continue
                    result = value.get('Result')
                    if result:
                        if result.strip() == '':
                            result = None
                    else:
                        result = None

                    retested = value.get('Retested')

                    uncertainty = None
                    service = analysis.getService()

                    if result:
                        precision = service.getPrecision()
                        if precision:
                            result = self.get_precise_result(result, precision)

                        uncertainty = self.get_uncertainty(result, service)

                    titrationvolume = value.get('TitrationVolume')
                    if titrationvolume:
                        if titrationvolume.strip() == '':
                            titrationvolume = None
                    else:
                        titrationvolume = None

                    titrationfactor = value.get('TitrationFactor')
                    if titrationfactor:
                        if titrationfactor.strip() == '':
                            titrationfactor = None
                    else:
                        titrationfactor = None

                    grossmass = value.get('GrossMass')
                    if grossmass:
                        if grossmass.strip() == '':
                            grossmass = None
                    else:
                        grossmass = None

                    netmass = value.get('NetMass')
                    if netmass:
                        if netmass.strip() == '':
                            netmass = None
                    else:
                        netmass = None

                    vesselmass = value.get('VesselMass')
                    if vesselmass:
                        if vesselmass.strip() == '':
                            vesselmass = None
                    else:
                        vesselmass = None

                    samplemass = value.get('SampleMass')
                    if samplemass:
                        if samplemass.strip() == '':
                            samplemass = None
                    else:
                        samplemass = None

                    analysis.setTitrationVolume(titrationvolume)
                    analysis.setTitrationFactor(titrationfactor)
                    analysis.setGrossMass(grossmass)
                    analysis.setNetMass(netmass)
                    analysis.setVesselMass(vesselmass)
                    analysis.setSampleMass(samplemass)

                    analysis.edit(
                        Result = result,
                        Retested = retested,
                        Uncertainty = uncertainty,
                        Unit = service.getUnit()
                    )

                    if analysis._affects_other_analysis:
                        self.get_dependant_results(analysis)
                    if result is None:
                        continue

                    try:
                        wf_tool.doActionFor(analysis, 'submit')
                        transaction_note('Changed status of %s at %s' % (
                            analysis.title_or_id(), analysis.absolute_url()))
                    except WorkflowException:
                        pass
            if self.context.getReportDryMatter():
                self.context.setDryMatterResults()

            review_state = wf_tool.getInfoFor(self.context, 'review_state', '')
            if review_state == 'to_be_verified':
                self.request.RESPONSE.redirect(self.context.absolute_url())
            else:
                self.request.RESPONSE.redirect(
                    '%s/analysisrequest_analyses' % self.context.absolute_url())
        else:
            return self.template()

    def get_dependant_results(self, this_child):
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=this_child
        ##title=Get analysis results dependant on other analyses results
        ##
        results = {}

        def test_reqs(reqd_calcs):
            all_results = True
            for reqd in reqds:
                if results[reqd] == None:
                    all_results = False
                    break
            return all_results

        def update_data(parent, result_in):
            if result_in == None:
                result = None
            else:
                result = '%.2f' % result_in
            service = parent.getService()

            uncertainty = self.get_uncertainty(result, service)
            parent.edit(
                Result = result,
                Uncertainty = uncertainty,
                Unit = service.getUnit()
            )
            return


        rc = getToolByName(self, 'reference_catalog');
        parents = [uid for uid in
                   rc.getBackReferences(this_child, 'AnalysisAnalysis')]
        for p in parents:
            parent = rc.lookupObject(p.sourceUID)

            parent_keyword = parent.getAnalysisKey()
            for child in parent.getDependantAnalysis():
                keyword = child.getAnalysisKey()
                try:
                    results[keyword] = Decimal(child.getResult())
                except:
                    results[keyword] = None

            result = None
            if parent_keyword[0:3] == 'AME':
                protein_type = parent_keyword[3:len(parent_keyword)]
                protein_keyword = 'ProteinCrude%s' % protein_type
                reqds = [protein_keyword, 'FatCrudeEtherExtraction', 'Starch', 'Sugars']
                if  test_reqs(reqds):
                    ProteinCrude = results[protein_keyword]
                    FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
                    Starch = results['Starch']
                    Sugars = results['Sugars']
                    result = (Decimal('0.1551') * ProteinCrude) + \
                           (Decimal('0.3431') * FatCrudeEtherExtraction) + \
                           (Decimal('0.1669') * Starch) + (Decimal('0.1301') * Sugars)
                else:
                    result = None
                update_data(parent, result)

            if parent_keyword[0:2] == 'ME':
                protein_type = parent_keyword[2:len(parent_keyword)]
                protein_keyword = 'ProteinCrude%s' % protein_type
                reqds = [protein_keyword, 'FatCrudeEtherExtraction', 'FibreCrude', 'Ash']
                if test_reqs(reqds):
                    ProteinCrude = results[protein_keyword]
                    FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
                    FibreCrude = results['FibreCrude']
                    Ash = results['Ash']
                    result = 12 + (Decimal('0.008') * ProteinCrude) + \
                           (Decimal('0.023') * FatCrudeEtherExtraction) - (Decimal('0.018') * FibreCrude) + \
                           (Decimal('0.012') * Ash)
                else:
                    result = None
                update_data(parent, result)

            if parent_keyword[0:3] == 'TDN':
                ME_type = parent_keyword[3:len(parent_keyword)]
                ME_keyword = 'ME%s' % ME_type
                reqds = [ME_keyword, ]
                if test_reqs(reqds):
                    ME = results[ME_keyword]
                    result = Decimal('6.67') * ME
                else:
                    result = None
                update_data(parent, result)

            if parent_keyword[0:3] == 'NSC':
                protein_type = parent_keyword[3:len(parent_keyword)]
                protein_keyword = 'ProteinCrude%s' % protein_type
                reqds = ['FibreNDF', protein_keyword, 'FatCrudeEtherExtraction', 'Ash']
                if test_reqs(reqds):
                    FibreNDF = results['FibreNDF']
                    ProteinCrude = results[protein_keyword]
                    FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
                    Ash = results['Ash']
                    result = 100 - (FibreNDF + ProteinCrude + \
                                    FatCrudeEtherExtraction + Ash)
                else:
                    result = None
                update_data(parent, result)

            if parent_keyword[0:2] == 'DE':
                protein_type = parent_keyword[2:len(parent_keyword)]
                protein_keyword = 'ProteinCrude%s' % protein_type
                reqds = [protein_keyword, 'FatCrudeEtherExtraction', 'FibreCrude', 'Ash']
                if test_reqs(reqds):
                    ProteinCrude = results[protein_keyword]
                    FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
                    FibreCrude = results['FibreCrude']
                    Ash = results['Ash']
                    result = Decimal('17.38') + (Decimal('0.105') * ProteinCrude) + \
                           (Decimal('0.114') * FatCrudeEtherExtraction) - (Decimal('0.317') * FibreCrude) - \
                           (Decimal('0.402') * Ash)
                else:
                    result = None
                update_data(parent, result)
                update_data(parent, result)

            drymatter = self.context.bika_settings.getDryMatterService()
            if parent.getServiceUID() == (hasattr(drymatter, 'UID') and drymatter.UID() or None):
                moisture = self.context.bika_settings.getMoistureService()
                moisture_key = moisture.getAnalysisKey()
                reqds = [moisture_key, ]
                if test_reqs(reqds):
                    Moisture = results[moisture_key]
                    result = Decimal('100') - Moisture
                else:
                    result = None
                update_data(parent, result)

            if parent_keyword == 'DryMatterWet':
                reqds = ['MoistureTotal', ]
                if test_reqs(reqds):
                    MoistureTotal = results['MoistureTotal']
                    result = Decimal('100') - MoistureTotal
                else:
                    result = None
                update_data(parent, result)

            if parent_keyword == 'MoistureTotal':
                reqds = ['MoistureWet', 'MoistureDry']
                if test_reqs(reqds):
                    MoistureWet = results['MoistureWet']
                    MoistureDry = results['MoistureDry']
                    result = MoistureWet + (MoistureDry * ((Decimal('100') - MoistureWet) / Decimal('100')))
                else:
                    result = None
                update_data(parent, result)

            if parent_keyword == 'ProteinKOH':
                if results.has_key('ProteinCrudeDumas'):
                    protein_keyword = 'ProteinCrudeDumas'
                else:
                    if results.has_key('ProteinCrudeKjeldahl'):
                        protein_keyword = 'ProteinCrudeKjeldahl'
                    else:
                        protein_keyword = 'ProteinCrude'
                reqds = [protein_keyword]
                if test_reqs(reqds):
                    ProteinCrude = results[protein_keyword]
                    Corrected = parent.getInterimResult('Corrected')
                    SKCorrFactor = parent.getInterimResult('SKCorrFactor')
                    if ProteinCrude and Corrected and SKCorrFactor:
                        Corrected = float(Corrected)
                        SKCorrFactor = float(SKCorrFactor)
                        parent.setInterimResult(protein_keyword, ProteinCrude)
                        result = Corrected / ProteinCrude * 100 * SKCorrFactor
                    else:
                        result = None
                        parent.setInterimResult(protein_keyword, None)
                update_data(parent, result)

            if parent_keyword == 'ProteinSoluble':
                if results.has_key('ProteinCrudeDumas'):
                    protein_keyword = 'ProteinCrudeDumas'
                else:
                    if results.has_key('ProteinCrudeKjeldahl'):
                        protein_keyword = 'ProteinCrudeKjeldahl'
                    else:
                        protein_keyword = 'ProteinCrude'
                reqds = [protein_keyword]
                if test_reqs(reqds):
                    ProteinCrude = results[protein_keyword]
                    Unadjusted = parent.getInterimResult('Unadjusted')
                    SKCorrFactor = parent.getInterimResult('SKCorrFactor')
                    if ProteinCrude and Unadjusted:
                        Unadjusted = float(Unadjusted)
                        parent.setInterimResult(protein_keyword, ProteinCrude)
                        result = ProteinCrude - Unadjusted
                    else:
                        result = None
                        parent.setInterimResult(protein_keyword, None)
                update_data(parent, result)

            if parent.checkHigherDependancies():
                self.get_dependant_results(parent)

        return

    def get_uncertainty(self, result, service):
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=result, service
        ##title=Get result uncertainty
        ##
        if result is None:
            return None

        uncertainties = service.getUncertainties()
        if uncertainties:
            try:
                result = float(result)
            except ValueError:
                # if it is not an float we assume no measure of uncertainty
                return None

            for d in uncertainties:
                if float(d['intercept_min']) <= result < float(d['intercept_max']):
                    return d['errorvalue']
            return None
        else:
            return None

    def get_precise_result(self, result, precision):
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=result, precision
        ##title=Return result as a string with the correct precision
        ##
        try:
            float_result = Decimal(result)
        except ValueError:
            return result

        if precision == None or precision == '':
            precision = 0
        if precision == 0:
            precise_result = '%.0f' % float_result
        if precision == 1:
            precise_result = '%.1f' % float_result
        if precision == 2:
            precise_result = '%.2f' % float_result
        if precision == 3:
            precise_result = '%.3f' % float_result
        if precision == 4:
            precise_result = '%.4f' % float_result
        if precision > 4:
            precise_result = '%.5f' % float_result
        return precise_result

    def get_analysis_request_actions(self):
        ## Script (Python) "get_analysis_request_actions"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=
        ##title=
        ##
        wf_tool = self.context.portal_workflow
        actions_tool = self.context.portal_actions

        actions = {}
        for analysis in self.context.getAnalyses():
            review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
            if review_state in ('not_requested', 'to_be_verified', 'verified'):
                a = actions_tool.listFilteredActionsFor(analysis)
                for action in a['workflow']:
                    if actions.has_key(action['id']):
                        continue
                    actions[action['id']] = action

        return actions.values()

class AnalysisRequestManageResultsNotRequestedView(AnalysisRequestManageResultsView):
    template = ViewPageTemplateFile("templates/analysisrequest_analyses_not_requested.pt")

    def __call__(self):
        return self.template()


class AnalysisRequestContactCCs(BrowserView):
    """ Returns lists of UID/Title for preconfigured CC contacts 
        When a client contact is selected from the #contact dropdown,
        the dropdown's ccuids attribute is set to the Contact UIDS 
        returned here, and the #cc_titles textbox is filled with Contact Titles
    """
    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        uid = self.request.form.keys() and self.request.form.keys()[0] or None
        if not uid:
            return
        contact = rc.lookupObject(uid)
        cc_uids = []
        cc_titles = []
        for cc in contact.getCCContact():
            cc_uids.append(cc.UID())
            cc_titles.append(cc.Title())
        return json.dumps([",".join(cc_uids), ",".join(cc_titles)])

class AnalysisRequestSelectCCView(BikaListingView):
    """ The CC Selector popup window uses this view"""
    contentFilter = {'portal_type': 'Contact'}
    content_add_buttons = {}
    title = "Contacts to CC"
    description = ''
    show_editable_border = False
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = False
    pagesize = 20

    columns = {
        'getFullname': {'title': _('Full Name')},
        'getEmailAddress': {'title': _('Email Address')},
        'getBusinessPhone': {'title': _('Business Phone')},
        'getMobilePhone': {'title': _('Mobile Phone')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns': ['getFullname',
                     'getEmailAddress',
                     'getBusinessPhone',
                     'getMobilePhone'],
         'buttons':[{'cssclass': 'context select_cc_select',
                     'title': _('Add to CC list'),
                     'url': ''}]},
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        out = []
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            if items[x]['UID'] in self.request.get('hide_uids', ''): continue
            if items[x]['UID'] in self.request.get('selected_uids', ''):
                items[x]['checked'] = True
            out.append(items[x])
        return out

class AnalysisRequestSelectSampleView(BikaListingView):
    contentFilter = {'portal_type': 'Sample'}
    content_add_buttons = {}
    show_editable_border = False
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = False
    batch = True
    pagesize = 50

    columns = {
        'getSampleID': {'title': _('Sample ID'), 'table_row_class':'select_sample_select'},
        'getClientSampleID': {'title': _('Client SID')},
        'getClientReference': {'title': _('Client Reference')},
        'SampleType': {'title': _('Sample Type')},
        'SamplePoint': {'title': _('Sample Point')},
        'getDateReceived': {'title': _('Date Received')},
        'state_title': {'title': _('State')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns': ['getSampleID',
                     'getClientSampleID',
                     'SampleType',
                     'SamplePoint',
                     'state_title']},
        {'title': _('Due'), 'id':'due',
         'columns': ['getSampleID',
                     'getClientSampleID',
                     'SampleType',
                     'SamplePoint']},
        {'title': _('Received'), 'id':'received',
         'columns': ['getSampleID',
                     'getClientSampleID',
                     'SampleType',
                     'SamplePoint',
                     'getDateReceived']},
    ]

    def __init__(self, context, request):
        super(AnalysisRequestSelectSampleView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Samples"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        out = []
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            if items[x]['UID'] in self.request.get('hide_uids', ''): continue
            if items[x]['UID'] in self.request.get('selected_uids', ''):
                items[x]['checked'] = True
            items[x]['view_url'] = obj.absolute_url() + "/view"
            items[x]['SampleType'] = obj.getSampleType().Title()
            items[x]['SamplePoint'] = obj.getSamplePoint() and obj.getSamplePoint().Title()
            items[x]['getDateReceived'] = obj.getDateReceived() and self.context.toLocalizedTime(obj.getDateReceived(), long_format = 0) or ''
            items[x]['getDateSampled'] = obj.getDateSampled() and self.context.toLocalizedTime(obj.getDateSampled(), long_format = 0) or ''
            items[x]['item_data'] = json.dumps({
                'SampleID': items[x]['Title'],
                'ClientReference': items[x]['getClientReference'],
                'ClientSampleID': items[x]['getClientSampleID'],
                'DateReceived': items[x]['getDateReceived'],
                'DateSampled': items[x]['getDateSampled'],
                'SampleType': items[x]['SampleType'],
                'SamplePoint': items[x]['SamplePoint'],
                'field_analyses': self.FieldAnalyses(obj),
                'column': self.request.get('column', None),
            })
            out.append(items[x])
        return out

    def FieldAnalyses(self, sample):
        """ Returns a dictionary of lists reflecting Field Analyses
            linked to this sample.
            For secondary ARs field analyses and their values are 
            read/written from the first AR.
            {category_uid: [service_uid, service_uid], ... }
        """
        res = {}
        ars = sample.getAnalysisRequests()
        if len(ars) > 0:
            for analysis in ars[0].getAnalyses():
                if analysis.getService().getPointOfCapture() == 'field':
                    catuid = analysis.getService().getCategoryUID()
                    if res.has_key(catuid):
                        res[catuid].append(analysis.getService().UID())
                    else:
                        res[catuid] = [analysis.getService().UID()]
        return res

class AnalysisRequest_AnalysisServices(BrowserView):
    """ AJAX requests pull this data for insertion when category header rows are clicked.
        The view returns a standard pagetemplate, the entire html of which is inserted.
    """
    template = ViewPageTemplateFile("templates/analysisrequest_analysisservices.pt")
    def __call__(self):
        return self.template()

    def Services(self, CategoryUID, poc):
        """ return a list of brains
        """
        pc = getToolByName(self, 'portal_catalog')
        return pc(portal_type = "AnalysisService", getCategoryUID = CategoryUID, getPointOfCapture = poc)

    def CalcDependancy(self, column, serviceUID):
        """ return {'categoryIDs': [element IDs of category TRs], 
                    'serviceUIDs': [dependant service UIDs]}
        """
        pc = getToolByName(self, 'portal_catalog')
        rc = getToolByName(self, 'reference_catalog')
        service = rc.lookupObject(serviceUID)
        depcatIDs = []
        depUIDs = []
        for depUID in service.getCalcDependancyUIDS():
            dep_service = rc.lookupObject(depUID)
            depcat_id = dep_service.getCategoryUID() + "_" + dep_service.PointOfCapture
            if depcat_id not in depcatIDs: depcatIDs.append(depcat_id)
            depUIDs.append(depUID)
        return {'categoryIDs':depcatIDs, 'serviceUIDs':depUIDs}

class AnalysisRequest_ProfileServices(BrowserView):
    """ AJAX requests pull this to retrieve a list of services in an AR Profile.
        return JSON data {categoryUID: [serviceUID,serviceUID], ...}
    """
    def __call__(self):
        rc = getToolByName(self, 'reference_catalog')
        pc = getToolByName(self, 'portal_catalog')
        profile = rc.lookupObject(self.request['profileUID'])
        if not profile: return

        services = {}
        for service in profile.getService():
            service = pc(portal_type = "AnalysisService", UID = service.UID())[0]
            categoryUID = service.getCategoryUID
            poc = service.getPointOfCapture
            try: services["%s_%s" % (categoryUID, poc)].append(service.UID)
            except: services["%s_%s" % (categoryUID, poc)] = [service.UID, ]
        return json.dumps(services)

class AnalysisRequest_SampleTypes(BrowserView):
    """ autocomplete data source for sample types field
        return JSON data [string,string]
    """
    def __call__(self):
        pc = getToolByName(self, 'portal_catalog')
        term = self.request.get('term', '')
        items = [s.Title for s in pc(portal_type = "SampleType") if s.Title.find(term) > -1]
        return json.dumps(items)

class AnalysisRequest_SamplePoints(BrowserView):
    """ autocomplete data source for sample points field
        return JSON data [string,string]
    """
    def __call__(self):
        pc = getToolByName(self, 'portal_catalog')
        term = self.request.get('term', '')
        items = [s.Title for s in pc(portal_type = "SamplePoint") if s.Title.find(term) > -1]
        return json.dumps(items)

def analysisrequest_add_submit(context, request):

    form = request.form
    portal = getToolByName(context, 'portal_url').getPortalObject()
    rc = getToolByName(context, 'reference_catalog')
    wftool = getToolByName(context, 'portal_workflow')
    pc = getToolByName(context, 'portal_catalog')
    came_from = form.has_key('came_from') and form['came_from'] or 'add'

#    import pprint
#    pprint.pprint(form)

    errors = {}
    def error(field = None, column = None, message = None):
        if not message:
            message = context.translate('message_input_required',
                                        default = 'Input is required but no input given.',
                                        domain = 'bika')
        column = column or ""
        field = field or ""
        error_key = field and column and "%s.%s" % (column, field) or 'form error'
        errors[error_key] = message

    # first some basic validation
    has_analyses = False
    for column in range(int(form['col_count'])):
        column = "%01d" % column
        if form.has_key("ar.%s" % column) and form["ar.%s" % column].has_key("Analyses"):
            has_analyses = True
    if not has_analyses or not form.has_key('Prices'):
        error(message = _("No analyses have been selected."))
        return json.dumps({'errors': errors})

    prices = form['Prices']
    vat = form['VAT']

    required = ['Analyses']
    if came_from == "add": required += ['SampleType', 'DateSampled']
    fields = ('SampleID', 'ClientOrderNumber', 'ClientReference',
              'ClientSampleID', 'DateSampled', 'SampleType', 'SamplePoint',
              'ReportDryMatter', 'InvoiceExclude', 'Analyses')

    for column in range(int(form['col_count'])):
        column = "%01d" % column
        if not form.has_key("ar.%s" % column):
            continue
        ar = form["ar.%s" % column]
        if len(ar.keys()) == 3: # three empty price fields
            continue
        # check that required fields have values
        for field in required:
            if not ar.has_key(field):
                error(field, column)

        # validate all field values
        for field in fields:
            # ignore empty field values
            if not ar.has_key(field):
                continue

            if came_from == "add" and field == "SampleID":
                if not pc(portal_type = 'Sample',
                          getSampleID = ar[field]):
                    error(field, column, '%s is not a valid sample ID' % ar[field])

            elif came_from == "add" and field == "SampleType":
                if not pc(portal_type = 'SampleType',
                          Title = ar[field]):
                    error(field, column, '%s is not a valid sample type' % ar[field])

            elif came_from == "add" and field == "SamplePoint":
                if not pc(portal_type = 'SamplePoint',
                          Title = ar[field]):
                    error(field, column, '%s is not a valid sample point' % ar[field])

            #elif field == "ReportDryMatter":
            #elif field == "InvoiceExclude":
            # elif field == "DateSampled":
            # XXX Should we check that these three are unique? :
            #elif field == "ClientOrderNumber":
            #elif field == "ClientReference":
            #elif field == "ClientSampleID":

    if errors:
        return json.dumps({'errors':errors})

    ARs = []
    services = {} # UID:service

    # The actual submission

    for column in range(int(form['col_count'])):
        if not form.has_key("ar.%s" % column):
            continue
        values = form["ar.%s" % column].copy()
        if len(values.keys()) == 3:
            continue

        ar_number = 1
        sample_state = 'due'

        profile = None
        if (values.has_key('ARProfile')):
            profileUID = values['ARProfile']
            for proxy in pc(portal_type = 'ARProfile',
                            UID = profileUID):
                profile = proxy.getObject()
            if profile == None:
                for proxy in pc(portal_type = 'LabARProfile',
                                UID = profileUID):
                    profile = proxy.getObject()

        if values.has_key('SampleID'):
            # Secondary AR
            sample_id = values['SampleID']
            sample_proxy = pc(portal_type = 'Sample',
                              getSampleID = sample_id)
            assert len(sample_proxy) == 1
            sample = sample_proxy[0].getObject()
            ar_number = sample.getLastARNumber() + 1
            wf_tool = context.portal_workflow
            sample_state = wf_tool.getInfoFor(sample, 'review_state', '')
            sample.edit(LastARNumber = ar_number)
            sample.reindexObject()
        else:
            # Primary AR or AR Edit both come here
            if came_from == "add":
                sample_id = context.generateUniqueId('Sample')
                context.invokeFactory(id = sample_id, type_name = 'Sample')
                sample = context[sample_id]
                sample.edit(
                    SampleID = sample_id,
                    LastARNumber = ar_number,
                    DateSubmitted = DateTime(),
                    SubmittedByUser = sample.current_user(),
                    **dict(values)
                )
            else:
                sample = context.getSample()
                sample.edit(
                    **dict(values)
                )
            dis_date = sample.disposal_date()
            sample.setDisposalDate(dis_date)
        sample_uid = sample.UID()

        # create AR

        Analyses = values['Analyses']
        del values['Analyses']

        if came_from == "add":
            ar_id = context.generateARUniqueId('AnalysisRequest', sample_id, ar_number)
            context.invokeFactory(id = ar_id, type_name = 'AnalysisRequest')
            ar = context[ar_id]
            ar.edit(
                RequestID = ar_id,
                DateRequested = DateTime(),
                Contact = form['Contact'],
                CCContact = form['cc_uids'].split(","),
                CCEmails = form['CCEmails'],
                Sample = sample_uid,
                Profile = profile,
                **dict(values)
            )
        else:
            ar_id = context.getRequestID()
            ar = context
            ar.edit(
                Contact = form['Contact'],
                CCContact = form['cc_uids'].split(","),
                CCEmails = form['CCEmails'],
                Profile = profile,
                **dict(values)
            )

        ar.setAnalyses(['%s:%s' % (a, prices[a]) for a in Analyses])

        if (values.has_key('profileTitle')):
            profile_id = context.generateUniqueId('ARProfile')
            context.invokeFactory(id = profile_id, type_name = 'ARProfile')
            profile = context[profile_id]
            ar.edit(Profile = profile)
            profile.setProfileTitle(values['profileTitle'])
            analyses = ar.getAnalyses()
            services_array = []
            for a in analyses:
                services_array.append(a.getServiceUID())
            profile.setService(services_array)
            profile.reindexObject()

        if values.has_key('SampleID') and wftool.getInfoFor(sample, 'review_state') != 'due':
            wftool.doActionFor(ar, 'receive')

        ARs.append(ar_id)

    # AVS check sample_state and promote the AR is > 'due'

#if primaryArUIDs:
#   context.REQUEST.SESSION.set('uids', primaryArUIDs)
#   return state.set(status='print')

    if came_from == "add":
        if len(ARs) > 1:
            message = context.translate('message_ars_created',
                                        default = 'Analysis requests ${ARs} were successfully created.',
                                        mapping = {'ARs': ', '.join(ARs)}, domain = 'bika')
        else:
            message = context.translate('message_ar_created',
                                        default = 'Analysis request ${AR} was successfully created.',
                                        mapping = {'AR': ', '.join(ARs)}, domain = 'bika')
    else:
        message = "Changes Saved."

    context.plone_utils.addPortalMessage(message, 'info')
    return json.dumps({'success':message})
