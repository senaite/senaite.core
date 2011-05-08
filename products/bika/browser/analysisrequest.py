from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from DateTime import DateTime
import json

def analysisrequest_add_submit(context, request):

    form = request.form
    portal = getToolByName(context, 'portal_url').getPortalObject()
    rc = getToolByName(context, 'reference_catalog')
    pc = getToolByName(context, 'portal_catalog')
    came_from = form.has_key('came_from') and form['came_from'] or 'add'

    import pprint
    pprint.pprint(request.form)

    errors = {}
    def error(field = None, column = None, message = None):
        if not message:
            message = context.translate('message_input_required',
                                        default = 'Input is required but no input given.',
                                        domain = 'bika')
        colstr = column != None and "%s." % column or ""
        fieldstr = field != None and field or ""
        error_key = "%s%s" % (colstr, field) or 'Form error'
        try: errors[error_key].append(message)
        except: errors[error_key] = [message, ]

    # first some basic validation

    required = ['Analyses']
    if came_from == "add": required += ['SampleType', 'DateSampled']
    fields = ('SampleID', 'ClientOrderNumber', 'ClientReference',
              'ClientSampleID', 'DateSampled', 'SampleType', 'SamplePoint',
              'ReportDryMatter', 'InvoiceExclude', 'Analyses')

    try:
        prices = form['Prices']
        vat = form['VAT']
    except KeyError:
        return error(message = "No analyses selected.")

    for column in range(int(form['col_count'])):
        if not form.has_key("ar.%s" % column):
            continue
        ar = form["ar.%s" % column]
        if len(ar.keys()) == 3:
            continue

        # check that required fields have values
        for field in required:
            if not ar.has_key(field):
                error(column, field)

        # validate all field values
        for field in fields:
            # ignore empty field values
            if not ar.has_key(field):
                continue

            if came_from == "add" and field == "SampleID":
                if not pc(portal_type = 'Sample',
                          getSampleID = ar[field]):
                    error(column, field, '%s is not a valid sample ID' % ar[field])

            elif came_from == "add" and field == "SampleType":
                if not pc(portal_type = 'SampleType',
                          Title = ar[field]):
                    error(column, field, '%s is not a valid sample type' % ar[field])

            elif came_from == "add" and field == "SamplePoint":
                if not pc(portal_type = 'SamplePoint',
                          Title = ar[field]):
                    error(column, field, '%s is not a valid sample point' % ar[field])

            #elif field == "ReportDryMatter":
            #elif field == "InvoiceExclude":
            # elif field == "DateSampled":
            # XXX Should we check that these three are unique? :
            #elif field == "ClientOrderNumber":
            #elif field == "ClientReference":
            #elif field == "ClientSampleID":

    if errors:
        print "errors: ", errors
        return json.dumps(errors)

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
            sample_uid = values['SampleUID']
            sample_proxy = pc(portal_type = 'Sample',
                              getSampleID = sample_id)
            assert len(sample_proxy) == 1
            sample = sample_proxy[0].getObject()
            ar_number = sample.getLastARNumber() + 1
            wf_tool = context.portal_workflow
            sample_state = wf_tool.getInfoFor(sample,
                                              'review_state', '')
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
            sample_uid = sample.UID()
            dis_date = sample.disposal_date()
            sample.setDisposalDate(dis_date)

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

        ARs.append(ar_id)

    # AVS check sample_state and promote the AR is > 'due'

    if came_from == "add":
        return "Successfully created new AR%s" % (len(ARs) > 1 and 's' or '')
    else:
        return "Changes Saved"



class AnalysisRequestViewView(BrowserView):
    """ AR View form
    """
    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")

    #def __init__(self, context, request):
    #    super(BrowserView, self).__init__(context, request)
    #    request.set('disable_border', 1)

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
        for analysis in pc(portal_type = "Analysis"):
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
                spec_min = float(spec[aservice]['min'])
                spec_max = float(spec[aservice]['max'])
                if spec_min <= result <= spec_max:
                    result_class = ''
                #else:
                #    """ check if in error range """
                #    error_amount = result * float(spec[aservice]['error']) / 100
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
                if (result < float(spec['min'])) or (result > float(spec['max'])):
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
            analysisrequest_add_submit(self.context, self.request)
        else:
            return self.template()

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
        for analysis in pc(portal_type = "Analysis", RequestID = self.context.RequestID):
            analysis = analysis.getObject() # XXX getObject
            service = analysis.getService()
            res.append([service.getCategoryUID(), service.UID(), service.getPointOfCapture()])
        return res

class AnalysisRequestManageResultsView(AnalysisRequestViewView):
    template = ViewPageTemplateFile("templates/analysisrequest_analyses.pt")

    def __call__(self):
        if self.request.form.has_key("submitted"):
            """ Submit results
            """
            wf_tool = getToolByName(self, 'portal_workflow')

            for key, value in self.request.form.items():
                if key.startswith('results'):
                    id = key.split('.')[-1]
                    analysis = self._getOb(id)
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

                    wf_tool.doActionFor(analysis, 'submit')
                    transaction_note('Changed status of %s at %s' % (
                        analysis.title_or_id(), analysis.absolute_url()))

            if self.getReportDryMatter():
                self.setDryMatterResults()

            review_state = wf_tool.getInfoFor(self, 'review_state', '')
            if review_state == 'to_be_verified':
                self.request.RESPONSE.redirect(self.absolute_url())
            else:
                self.request.RESPONSE.redirect(
                    '%s/analysisrequest_analyses' % self.absolute_url())
        else:
            return self.template()

    def submitResults(self):
        print "asdfasdf SUBMITRESULTS"

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

class AnalysisRequestContactCCs(BrowserView):
    """ Returns lists of UID/Title for preconfigured CC contacts 
        When a client contact is selected from the #contact dropdown,
        the dropdown's ccuids attribute is set to the Contact UIDS 
        returned here, and the #cc_titles textbox is filled with Contact Titles
    """
    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        uid = self.request.form.keys()[0]
        contact = rc.lookupObject(uid)
        cc_uids = []
        cc_titles = []
        for cc in contact.getCCContact():
            cc_uids.append(cc.UID())
            cc_titles.append(cc.Title())
        return json.dumps([",".join(cc_uids), ",".join(cc_titles)])

class AnalysisRequestSelectCCView(BrowserView):
    """ The CC Selector popup window uses this view
    """
    template = ViewPageTemplateFile("templates/analysisrequest_select_cc.pt")
    def __call__(self):
        return self.template()

class AnalysisRequestSelectSampleView(BrowserView):
    """ The Sample Selector popup window uses this view
    """
    template = ViewPageTemplateFile("templates/analysisrequest_select_sample.pt")
    def Samples(self, client):
        pc = getToolByName(self.context, 'portal_catalog')
        return pc(portal_type = "Sample", getClient = client)

    def __call__(self):
        return self.template()

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
