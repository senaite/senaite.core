from AccessControl import Unauthorized
from bika.lims.browser.client import ClientAnalysisRequestsView
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import POINTS_OF_CAPTURE
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from zope.component import getMultiAdapter
from decimal import Decimal
from zope.interface import implements
from plone.app.content.browser.interfaces import IFolderContentsView
import plone
#from plone.protect import CheckAuthenticator
import json

class AnalysisRequestAnalysesView(BikaListingView):
    """ Displays a list of Analyses in a table.
        All InterimFields from all analyses are added to self.columns[].
        allow_edit boolean decides if edit is possible, but each analysis
        can be editable or not, depending on it's review_state.
        Keyword arguments are passed directly to portal_catalog.
    """
    content_add_actions = {}
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = False
    pagesize = 1000
    columns = {
        'Service': {'title': _('Analysis')},
        'WorksheetNumber': {'title': _('Worksheet')},
        'Result': {'title': _('Result')},
        'Uncertainty': {'title': _('+-')},
        'Attachments': {'title': _('Attachments')},
        'state_title': {'title': _('State')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns':['Service',
                    'state_title',
                    'WorksheetNumber',
                    'Result',
                    'Uncertainty',
                    'Attachments'],
         },
    ]
    def __init__(self, context, request, allow_edit=False, **kwargs):
        super(AnalysisRequestAnalysesView, self).__init__(context, request)
        self.allow_edit = allow_edit
        self.contentFilter = dict(kwargs)
        self.contentFilter['portal_type'] = 'Analysis'

    def folderitems(self):
        """ InterimFields are inserted into self.columns before the column called 'Result',
            not specifically ordered but vaguely predictable.
        """
        analyses = BikaListingView.folderitems(self)

        items = []
        self.interim_fields = {}
        for item in analyses:
            if not item.has_key('brain'): continue
            obj = item['brain'].getObject()
            item['Service'] = obj.getService().Title()
            item['WorksheetNumber'] = obj.getWorksheet()
            item['Uncertainty'] = obj.getUncertainty()
            item['Unit'] = obj.getUnit()
            item['Result'] = obj.getResult()
            item['Attachments'] = ", ".join([a.Title() for a in obj.getAttachment()])
            item['_allow_edit'] = self.allow_edit or False
            item['_calculation'] = obj.getService().getCalculation() or False
            interim_fields = obj.getInterimFields()
            item['item_data'] = json.dumps(interim_fields)

            # Add this analysis' interim fields to the list
            for i in interim_fields:
                if i['id'] not in self.interim_fields.keys():
                    self.interim_fields[i['id']] = i['title']
                # This InterimField dictionary is the item's column value.
                item[i['id']] = i

            items.append(item)

        interim_keys = self.interim_fields.keys()
        interim_keys.reverse()

        # munge self.columns
        for col_id in interim_keys:
            if col_id not in self.columns:
                self.columns[col_id] = {'title': self.interim_fields[col_id]}

        # munge self.review_states
        munged_states = []
        for state in self.review_states:
            pos = state['columns'].index('Result')
            if not pos: pos = len(state['columns'])
            for col_id in interim_keys:
                if col_id not in state['columns']:
                    state['columns'].insert(pos, col_id)
            munged_states.append(state)
        self.review_states = munged_states
        return items

class AnalysisRequestViewView(BrowserView):
    """ AR View form
        The AR fields are printed in a table, using analysisrequest_view.py
    """
#lab_accredited python:context.bika_settings.laboratory.getLaboratoryAccredited();
#profile python:here.getProfile() and here.getProfile().getProfileTitle() or '';
#global tf python:0;
#global out_of_range python:0;
#global dry_matter python:here.getReportDryMatter() and 1 or 0;
#global late python:0;
#client nocall:here/aq_parent;
#client_uid client/UID;
#member_groups python: [here.portal_groups.getGroupById(group.id).getGroupName() for group in here.portal_groups.getGroupsByUserId(member.id)];
#is_client python: 'clients' in member_groups;
#default_spec python:is_client and 'client' or 'lab';
#specification python:request.get('specification', default_spec);
#view_worksheets python:member.has_role(('Manager', 'LabManager', 'LabClerk', 'LabTechnician'));
#attachments_allowed here/bika_settings/getAttachmentsPermitted;
#ar_attach_allowed here/bika_settings/getARAttachmentsPermitted;
#analysis_attach_allowed here/bika_settings/getAnalysisAttachmentsPermitted;
#ar_review_state python:context.portal_workflow.getInfoFor(here, 'review_state', '');
#attachments here/getAttachment | nothing;
#delete_attachments python:False;
#update_attachments python:False">

    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")

    def __init__(self, context, request):
        super(AnalysisRequestViewView, self).__init__(context, request)
        self.FieldAnalysesView = AnalysisRequestAnalysesView(
                                context, request, getPointOfCapture = 'field')
        self.LabAnalysesView = AnalysisRequestAnalysesView(
                                context, request, getPointOfCapture = 'lab')

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
        """ Returns a dictionary with a list of field analyses and a list of lab analyses.
            This returns only categories which have analyses selected in the current AR.
            Categories which are not used by analyses in this AR are omitted
            Dictionary keys: field/lab
            Dictionary values: (Category Title,category UID)
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

    def getDefaultSpec(self):
        """ Returns 'lab' or 'client' to set the initial value of the specification radios """
        mt = getToolByName(self.context, 'portal_membership')
        pg = getToolByName(self.context, 'portal_groups')
        member = mt.getAuthenticatedMember();
        member_groups = [pg.getGroupById(group.id).getGroupName() for group in pg.getGroupsByUserId(member.id)]
        default_spec = ('clients' in member_groups) and 'client' or 'lab'
        return default_spec

    @property
    def review_state(self):
        return self.context.portal_workflow.getInfoFor(self.context, 'review_state', '')

    def getARProfileTitle(self):
        return self.context.getProfile() and here.getProfile().getProfileTitle() or '';


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

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.col_count = 4
        self.came_from = "add"
        self.DryMatterService = self.context.bika_settings.getDryMatterService()

    def __call__(self):
        if self.request.form.has_key("submitted"):
            return AJAXAnalysisRequestSubmit(self.context, self.request)()
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
            profiles.append(proxy.getObject())
        for proxy in pc(portal_type = 'LabARProfile', sort_on = 'sortable_title'):
            profile = proxy.getObject()
            profile.setTitle("Lab: %s" % profile.Title())
            profiles.append(proxy.getObject())
        return profiles

    def Categories(self):
        """ Dictionary keys: poc
            Dictionary values: (Category UID,category Title)
        """
        pc = getToolByName(self.context, 'portal_catalog')
        cats = {}
        for service in pc(portal_type = "AnalysisService"):
            service = service.getObject()
            poc = service.getPointOfCapture()
            if not cats.has_key(poc): cats[poc] = []
            category = service.getCategory()
            cat = (category.UID(), category.Title())
            if cat not in cats[poc]:
                cats[poc].append(cat)
        return cats

class AnalysisRequestEditView(AnalysisRequestAddView):
    template = ViewPageTemplateFile("templates/analysisrequest_edit.pt")

    def __init__(self, context, request):
        super(AnalysisRequestEditView, self).__init__(context, request)
        self.col_count = 1
        self.came_from = "edit"

    def SelectedServices(self):
        """ return information about services currently selected in the context AR.
            [[PointOfCapture, category uid, service uid],
             [PointOfCapture, category uid, service uid], ...]
        """
        pc = getToolByName(self.context, 'portal_catalog')
        res = []
        for analysis in pc(portal_type = "Analysis", getRequestID = self.context.RequestID):
            analysis = analysis.getObject()
            service = analysis.getService()
            res.append([service.getPointOfCapture(), service.getCategoryUID(), service.UID()])
        return res

class AnalysisRequestManageResultsView(AnalysisRequestViewView):
    template = ViewPageTemplateFile("templates/analysisrequest_manage_results.pt")

    def __init__(self, context, request):
        super(AnalysisRequestViewView, self).__init__(context, request)
        self.FieldAnalysesView = AnalysisRequestAnalysesView(
                               context, request, allow_edit=True, getPointOfCapture = 'field')
        self.LabAnalysesView = AnalysisRequestAnalysesView(
                               context, request, allow_edit=True, getPointOfCapture = 'lab')

    def __call__(self):
        wf_tool = getToolByName(self.context, 'portal_workflow')
        pc = getToolByName(self.context, 'portal_catalog')

        form = self.request.form
        if form.has_key("submitted"):
            import pprint
            pprint.pprint(form)

        return self.template()

    def getHazardous(self):
        return self.context.getSample().getSampleType().getHazardous()

##    def getInterimFields(self,PointOfCapture):
##        # Return all interim fields for all analyses in the self.`PointOfCapture`.
##        if PointOfCapture == 'field': return self.FieldAnalysesView.interim_fields
##        else: return self.LabAnalysesView.interim_fields
##
##         XXX event subscriber for AR publish
##        if only some analyses were published we still send an email
##        if workflow_action in ['publish', 'republish', 'prepublish'] and \
##            self.context.portal_type == 'AnalysisRequest' and \
##            len(success.keys()) > 0:
##            contact = self.context.getContact()
##            analysis_requests = [self.context]
##            contact.publish_analysis_requests(self.context, contact, analysis_requests, None)
##            # cc contacts
##            for cc_contact in self.context.getCCContact():
##                contact.publish_analysis_requests(self.context, cc_contact, analysis_requests, None)
##            # cc emails
##            cc_emails = self.context.getCCEmails()
##            if cc_emails:
##                contact.publish_analysis_requests(self.context, None, analysis_requests, cc_emails)
##        transaction_note(str(ids) + ' transitioned ' + workflow_action)
##
##
##            for key, value in form.items():
##                if key.startswith('results'):
##                    id = key.split('results.')[-1]
##                    analysis = pc(path = { "query": [self.context.id], "level" : 3 },
##                                    id = id)[0].getObject()
##                    if analysis.getCalcType() == 'dep':
##                        continue
##                    result = value.get('Result')
##                    if result:
##                        if result.strip() == '':
##                            result = None
##                    else:
##                        result = None
##
##                    retested = value.get('Retested')
##
##                    uncertainty = None
##                    service = analysis.getService()
##
##                    if result:
##                        precision = service.getPrecision()
##                        if precision:
##                            result = self.get_precise_result(result, precision)
##
##                        uncertainty = self.get_uncertainty(result, service)
##
##                    titrationvolume = value.get('TitrationVolume')
##                    if titrationvolume:
##                        if titrationvolume.strip() == '':
##                            titrationvolume = None
##                    else:
##                        titrationvolume = None
##
##                    titrationfactor = value.get('TitrationFactor')
##                    if titrationfactor:
##                        if titrationfactor.strip() == '':
##                            titrationfactor = None
##                    else:
##                        titrationfactor = None
##
##                    grossmass = value.get('GrossMass')
##                    if grossmass:
##                        if grossmass.strip() == '':
##                            grossmass = None
##                    else:
##                        grossmass = None
##
##                    netmass = value.get('NetMass')
##                    if netmass:
##                        if netmass.strip() == '':
##                            netmass = None
##                    else:
##                        netmass = None
##
##                    vesselmass = value.get('VesselMass')
##                    if vesselmass:
##                        if vesselmass.strip() == '':
##                            vesselmass = None
##                    else:
##                        vesselmass = None
##
##                    samplemass = value.get('SampleMass')
##                    if samplemass:
##                        if samplemass.strip() == '':
##                            samplemass = None
##                    else:
##                        samplemass = None
##
##                    analysis.setTitrationVolume(titrationvolume)
##                    analysis.setTitrationFactor(titrationfactor)
##                    analysis.setGrossMass(grossmass)
##                    analysis.setNetMass(netmass)
##                    analysis.setVesselMass(vesselmass)
##                    analysis.setSampleMass(samplemass)
##
##                    analysis.edit(
##                        Result = result,
##                        Retested = retested,
##                        Uncertainty = uncertainty,
##                        Unit = service.getUnit()
##                    )
##
##                    if analysis._affects_other_analysis:
##                        self.get_dependant_results(analysis)
##                    if result is None:
##                        continue
##
##                    try:
##                        wf_tool.doActionFor(analysis, 'submit')
##                        transaction_note('Changed status of %s at %s' % (
##                            analysis.title_or_id(), analysis.absolute_url()))
##                    except WorkflowException:
##                        pass
##            if self.context.getReportDryMatter():
##                self.context.setDryMatterResults()
##
##            review_state = wf_tool.getInfoFor(self.context, 'review_state', '')
##            if review_state == 'to_be_verified':
##                self.request.RESPONSE.redirect(self.context.absolute_url())
##            else:
##                self.request.RESPONSE.redirect(
##                    '%s/analysisrequest_analyses' % self.context.absolute_url())

##    def get_dependant_results(self, this_child):
##        ##bind container=container
##        ##bind context=context
##        ##bind namespace=
##        ##bind script=script
##        ##bind subpath=traverse_subpath
##        ##parameters=this_child
##        ##title=Get analysis results dependant on other analyses results
##        ##
##        results = {}

##        def test_reqs(reqd_calcs):
##            all_results = True
##            for reqd in reqds:
##                if results[reqd] == None:
##                    all_results = False
##                    break
##            return all_results
##
##        def update_data(parent, result_in):
##            if result_in == None:
##                result = None
##            else:
##                result = '%.2f' % result_in
##            service = parent.getService()
##
##            uncertainty = self.get_uncertainty(result, service)
##            parent.edit(
##                Result = result,
##                Uncertainty = uncertainty,
##                Unit = service.getUnit()
##            )
##            return
##
##
##        rc = getToolByName(self, 'reference_catalog');
##        parents = [uid for uid in
##                    rc.getBackReferences(this_child, 'AnalysisAnalysis')]
##        for p in parents:
##            parent = rc.lookupObject(p.sourceUID)
##
##            parent_keyword = parent.getAnalysisKey()
##            for child in parent.getDependantAnalysis():
##                keyword = child.getAnalysisKey()
##                try:
##                    results[keyword] = Decimal(child.getResult())
##                except:
##                    results[keyword] = None
##
##            result = None
##            if parent_keyword[0:3] == 'AME':
##                protein_type = parent_keyword[3:len(parent_keyword)]
##                protein_keyword = 'ProteinCrude%s' % protein_type
##                reqds = [protein_keyword, 'FatCrudeEtherExtraction', 'Starch', 'Sugars']
##                if  test_reqs(reqds):
##                    ProteinCrude = results[protein_keyword]
##                    FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
##                    Starch = results['Starch']
##                    Sugars = results['Sugars']
##                    result = (Decimal('0.1551') * ProteinCrude) + \
##                            (Decimal('0.3431') * FatCrudeEtherExtraction) + \
##                            (Decimal('0.1669') * Starch) + (Decimal('0.1301') * Sugars)
##                else:
##                    result = None
##                update_data(parent, result)
##
##            if parent_keyword[0:2] == 'ME':
##                protein_type = parent_keyword[2:len(parent_keyword)]
##                protein_keyword = 'ProteinCrude%s' % protein_type
##                reqds = [protein_keyword, 'FatCrudeEtherExtraction', 'FibreCrude', 'Ash']
##                if test_reqs(reqds):
##                    ProteinCrude = results[protein_keyword]
##                    FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
##                    FibreCrude = results['FibreCrude']
##                    Ash = results['Ash']
##                    result = 12 + (Decimal('0.008') * ProteinCrude) + \
##                            (Decimal('0.023') * FatCrudeEtherExtraction) - (Decimal('0.018') * FibreCrude) + \
##                            (Decimal('0.012') * Ash)
##                else:
##                    result = None
##                update_data(parent, result)
##
##            if parent_keyword[0:3] == 'TDN':
##                ME_type = parent_keyword[3:len(parent_keyword)]
##                ME_keyword = 'ME%s' % ME_type
##                reqds = [ME_keyword, ]
##                if test_reqs(reqds):
##                    ME = results[ME_keyword]
##                    result = Decimal('6.67') * ME
##                else:
##                    result = None
##                update_data(parent, result)
##
##            if parent_keyword[0:3] == 'NSC':
##                protein_type = parent_keyword[3:len(parent_keyword)]
##                protein_keyword = 'ProteinCrude%s' % protein_type
##                reqds = ['FibreNDF', protein_keyword, 'FatCrudeEtherExtraction', 'Ash']
##                if test_reqs(reqds):
##                    FibreNDF = results['FibreNDF']
##                    ProteinCrude = results[protein_keyword]
##                    FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
##                    Ash = results['Ash']
##                    result = 100 - (FibreNDF + ProteinCrude + \
##                                    FatCrudeEtherExtraction + Ash)
##                else:
##                    result = None
##                update_data(parent, result)
##
##            if parent_keyword[0:2] == 'DE':
##                protein_type = parent_keyword[2:len(parent_keyword)]
##                protein_keyword = 'ProteinCrude%s' % protein_type
##                reqds = [protein_keyword, 'FatCrudeEtherExtraction', 'FibreCrude', 'Ash']
##                if test_reqs(reqds):
##                    ProteinCrude = results[protein_keyword]
##                    FatCrudeEtherExtraction = results['FatCrudeEtherExtraction']
##                    FibreCrude = results['FibreCrude']
##                    Ash = results['Ash']
##                    result = Decimal('17.38') + (Decimal('0.105') * ProteinCrude) + \
##                            (Decimal('0.114') * FatCrudeEtherExtraction) - (Decimal('0.317') * FibreCrude) - \
##                            (Decimal('0.402') * Ash)
##                else:
##                    result = None
##                update_data(parent, result)
##                update_data(parent, result)
##
##            drymatter = self.context.bika_settings.getDryMatterService()
##            if parent.getServiceUID() == (hasattr(drymatter, 'UID') and drymatter.UID() or None):
##                moisture = self.context.bika_settings.getMoistureService()
##                moisture_key = moisture.getAnalysisKey()
##                reqds = [moisture_key, ]
##                if test_reqs(reqds):
##                    Moisture = results[moisture_key]
##                    result = Decimal('100') - Moisture
##                else:
##                    result = None
##                update_data(parent, result)
##
##            if parent_keyword == 'DryMatterWet':
##                reqds = ['MoistureTotal', ]
##                if test_reqs(reqds):
##                    MoistureTotal = results['MoistureTotal']
##                    result = Decimal('100') - MoistureTotal
##                else:
##                    result = None
##                update_data(parent, result)
##
##            if parent_keyword == 'MoistureTotal':
##                reqds = ['MoistureWet', 'MoistureDry']
##                if test_reqs(reqds):
##                    MoistureWet = results['MoistureWet']
##                    MoistureDry = results['MoistureDry']
##                    result = MoistureWet + (MoistureDry * ((Decimal('100') - MoistureWet) / Decimal('100')))
##                else:
##                    result = None
##                update_data(parent, result)
##
##            if parent_keyword == 'ProteinKOH':
##                if results.has_key('ProteinCrudeDumas'):
##                    protein_keyword = 'ProteinCrudeDumas'
##                else:
##                    if results.has_key('ProteinCrudeKjeldahl'):
##                        protein_keyword = 'ProteinCrudeKjeldahl'
##                    else:
##                        protein_keyword = 'ProteinCrude'
##                reqds = [protein_keyword]
##                if test_reqs(reqds):
##                    ProteinCrude = results[protein_keyword]
##                    Corrected = parent.getInterimResult('Corrected')
##                    SKCorrFactor = parent.getInterimResult('SKCorrFactor')
##                    if ProteinCrude and Corrected and SKCorrFactor:
##                        Corrected = float(Corrected)
##                        SKCorrFactor = float(SKCorrFactor)
##                        parent.setInterimResult(protein_keyword, ProteinCrude)
##                        result = Corrected / ProteinCrude * 100 * SKCorrFactor
##                    else:
##                        result = None
##                        parent.setInterimResult(protein_keyword, None)
##                update_data(parent, result)
##
##            if parent_keyword == 'ProteinSoluble':
##                if results.has_key('ProteinCrudeDumas'):
##                    protein_keyword = 'ProteinCrudeDumas'
##                else:
##                    if results.has_key('ProteinCrudeKjeldahl'):
##                        protein_keyword = 'ProteinCrudeKjeldahl'
##                    else:
##                        protein_keyword = 'ProteinCrude'
##                reqds = [protein_keyword]
##                if test_reqs(reqds):
##                    ProteinCrude = results[protein_keyword]
##                    Unadjusted = parent.getInterimResult('Unadjusted')
##                    SKCorrFactor = parent.getInterimResult('SKCorrFactor')
##                    if ProteinCrude and Unadjusted:
##                        Unadjusted = float(Unadjusted)
##                        parent.setInterimResult(protein_keyword, ProteinCrude)
##                        result = ProteinCrude - Unadjusted
##                    else:
##                        result = None
##                        parent.setInterimResult(protein_keyword, None)
##                update_data(parent, result)
##
##            if parent.checkHigherDependancies():
##                self.get_dependant_results(parent)
##        return


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

class AnalysisRequestResultsNotRequestedView(AnalysisRequestManageResultsView):
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
    content_add_actions = {}
    title = "Contacts to CC"
    description = ''
    show_editable_border = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
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

    def __init__(self, context, request):
        super(AnalysisRequestSelectCCView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Contacts to CC"))
        self.description = ""

    def __call__(self):
        return self.contents_table()

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
    content_add_actions = {}
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

    def __call__(self):
        return self.contents_table()

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

def getServiceDependencies(context,service_uid):
    """ Calculates the service dependencies, and returns them
        keyed by PointOfCapture and AnalysisCategory, in a
        funny little dictionary suitable for JSON/javascript
        consumption:
        {'pointofcapture_Point Of Capture':
            {  'categoryUID_categoryTitle':
                [ 'serviceUID_serviceTitle', 'serviceUID_serviceTitle', ...]
            }
        }
    """
    rc = getToolByName(context, 'reference_catalog')
    if not service_uid: return None
    service = rc.lookupObject(service_uid)
    if not service: return None
    calc = service.getCalculation()
    if not calc: return None
    deps = calc.getCalculationDependencies()

    result = {}

    def walk(deps):
        for service_uid,service_deps in deps.items():
            service = rc.lookupObject(service_uid)
            category = service.getCategory()
            cat = '%s_%s' % (category.UID(), category.Title())
            poc = '%s_%s' % (service.getPointOfCapture(), POINTS_OF_CAPTURE.getValue(service.getPointOfCapture()))
            srv = '%s_%s' % (service.UID(), service.Title())
            if not result.has_key(poc): result[poc] = {}
            if not result[poc].has_key(cat): result[poc][cat] = []
            result[poc][cat].append(srv)
            if service_deps:
                walk(service_deps)
    walk(deps)
    return result

class AJAXgetServiceDependencies():
    """ Return json(getServiceDependencies) """

    def __init__(self,context,request):
        self.context = context
        self.request = request

    def __call__(self):
        authenticator=getMultiAdapter((self.context, self.request), name=u"authenticator")
#        if not authenticator.verify(): raise Unauthorized
        result = getServiceDependencies(self.context, self.request.get('uid',''))
        if (not result) or (len(result.keys()) == 0):
            result = None
        return json.dumps(result)

class AJAXExpandCategory(BikaListingView):
    """ AJAX requests pull this view for insertion when category header rows are clicked/expanded. """
    template = ViewPageTemplateFile("templates/analysisrequest_analysisservices.pt")

    def __call__(self):
        authenticator=getMultiAdapter((self.context, self.request), name=u"authenticator")
#        if not authenticator.verify(): raise Unauthorized
        return self.template()

    def Services(self, poc, CategoryUID):
        """ return a list of services brains """
        pc = getToolByName(self, 'portal_catalog')
        services = pc(portal_type = "AnalysisService", getPointOfCapture = poc, getCategoryUID = CategoryUID)
        return services

class AJAXProfileServices(BrowserView):
    """ AJAX requests pull this to retrieve a list of services in an AR Profile.
        return JSON data {poc_categoryUID: [serviceUID,serviceUID], ...}
    """
    def __call__(self):
#        authenticator=getMultiAdapter((self.context, self.request), name=u"authenticator")
#        if not authenticator.verify(): raise Unauthorized
        rc = getToolByName(self, 'reference_catalog')
        pc = getToolByName(self, 'portal_catalog')

        profile = rc.lookupObject(self.request['profileUID'])
        if not profile: return

        services = {}
        for service in profile.getService():
            service = pc(portal_type = "AnalysisService", UID = service.UID())[0]
            categoryUID = service.getCategoryUID
            poc = service.getPointOfCapture
            try: services["%s_%s" % (poc,categoryUID)].append(service.UID)
            except: services["%s_%s" % (poc,categoryUID)] = [service.UID, ]

        return json.dumps(services)

def getBackReferences(context,service_uid):
    """ Recursively discover Calculation/DependentService backreferences from here.
        returns a list of Analysis Service objects

    """
    rc = getToolByName(context, REFERENCE_CATALOG)
    if not service_uid: return None
    service = rc.lookupObject(service_uid)
    if not service: return None

    services = []

    def walk(items):
        for item in items:
            if item.portal_type == 'AnalysisService':
                services.append(item)
            walk(item.getBackReferences())
    walk([service,])

    return services

class AJAXgetBackReferences():
    """ Return json(getBackReferences) """

    def __init__(self,context,request):
        self.context = context
        self.request = request

    def __call__(self):
        authenticator=getMultiAdapter((self.context, self.request), name=u"authenticator")
        #if not authenticator.verify(): raise Unauthorized
        result = getBackReferences(self.context, self.request.get('uid',''))
        if (not result) or (len(result) == 0):
            result = []
        return json.dumps([r.UID() for r in result])

class AJAXAnalysisRequestSubmit():

    def __init__(self,context,request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)

        if form.has_key("save_button"):
            portal = getToolByName(self.context, 'portal_url').getPortalObject()
            rc = getToolByName(self.context, 'reference_catalog')
            wftool = getToolByName(self.context, 'portal_workflow')
            pc = getToolByName(self.context, 'portal_catalog')
            came_from = form.has_key('came_from') and form['came_from'] or 'add'

            errors = {}
            def error(field = None, column = None, message = None):
                if not message:
                    message = self.context.translate('message_input_required',
                                                default = 'Input is required but no input given.',
                                                domain = 'bika')
                if (column or field):
                    error_key = " column: %s: %s" % (int(column)+1, field or '')
                else:
                    error_key = "Form Error"
                errors["Error"] = error_key + " " + message

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
                #elif field == "DateSampled":
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
                    wf_tool = self.context.portal_workflow
                    sample_state = wf_tool.getInfoFor(sample, 'review_state', '')
                    sample.edit(LastARNumber = ar_number)
                    sample.reindexObject()
                else:
                    # Primary AR or AR Edit both come here
                    if came_from == "add":
                        sample_id = self.context.generateUniqueId('Sample')
                        self.context.invokeFactory(id = sample_id, type_name = 'Sample')
                        sample = self.context[sample_id]
                        sample.edit(
                            SampleID = sample_id,
                            LastARNumber = ar_number,
                            DateSubmitted = DateTime(),
                            SubmittedByUser = sample.current_user(),
                            **dict(values)
                        )
                    else:
                        sample = self.context.getSample()
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
                    ar_id = self.context.generateARUniqueId('AnalysisRequest', sample_id, ar_number)
                    self.context.invokeFactory(id = ar_id, type_name = 'AnalysisRequest')
                    ar = self.context[ar_id]
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
                    ar_id = self.context.getRequestID()
                    ar = self.context
                    ar.edit(
                        Contact = form['Contact'],
                        CCContact = form['cc_uids'].split(","),
                        CCEmails = form['CCEmails'],
                        Profile = profile,
                        **dict(values)
                    )

                ar.setAnalyses(Analyses, prices=prices)

                if (values.has_key('profileTitle')):
                    profile_id = self.context.generateUniqueId('ARProfile')
                    self.context.invokeFactory(id = profile_id, type_name = 'ARProfile')
                    profile = self.context[profile_id]
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

            # XXX ARAnalysesField must move to content.analysis
            ar.setAnalyses(Analyses, prices=prices)

            if came_from == "add":
                if len(ARs) > 1:
                    message = self.context.translate('message_ars_created',
                                                default = 'Analysis requests ${ARs} were successfully created.',
                                                mapping = {'ARs': ', '.join(ARs)}, domain = 'bika')
                else:
                    message = self.context.translate('message_ar_created',
                                                default = 'Analysis request ${AR} was successfully created.',
                                                mapping = {'AR': ', '.join(ARs)}, domain = 'bika')
            else:
                message = "Changes Saved."
        else:
            message = "Changes Cancelled."

        self.context.plone_utils.addPortalMessage(message, 'info')
        return json.dumps({'success':message})

class AnalysisRequestsView(ClientAnalysisRequestsView):
    """ The main portal Analysis Requests action tab
        Only modifies the original attributes provided by ClientAnalysisRequestsView
    """
    show_editable_border = False
    content_add_actions = {}
    contentFilter = {'portal_type':'AnalysisRequest', 'path':{"query": ["/"], "level" : 0 }}
    title = "AnalysisRequests"
    description = ""

    def __init__(self, context, request):
        ClientAnalysisRequestsView.__init__(context, request)

        self.columns['Client'] = {'title': 'Client'}

        new_states = []
        for x in self.review_states:
            x['columns'] = ['Client'] + x['columns']
            new_states.append(x)
        self.review_states = new_states

    def folderitems(self):
        items = ClientAnalysisRequestsView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            items[x]['Client'] = items[x]['brain'].getObject().aq_parent.Title()
        return items


