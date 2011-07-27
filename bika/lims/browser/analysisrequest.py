from AccessControl import Unauthorized
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.client import ClientAnalysisRequestsView
from bika.lims.config import POINTS_OF_CAPTURE
from decimal import Decimal
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.component import getMultiAdapter
from zope.interface import implements,alsoProvides
import json
import plone

class AnalysisRequestViewView(BrowserView):
    """ AR View form
        The AR fields are printed in a table, using analysisrequest_view.py
    """

    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")

    def __init__(self, context, request):
        super(AnalysisRequestViewView, self).__init__(context, request)

    def __call__(self):
        self.Field = AnalysesView(self.context, self.request,
                                  getPointOfCapture = 'field').contents_table()
        self.Lab = AnalysesView(self.context, self.request,
                                getPointOfCapture = 'lab').contents_table()
        return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

    def now(self):
        return DateTime()

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

    def getHazardous(self):
        return self.context.getSample().getSampleType().getHazardous()

    def getARProfileTitle(self):
        return self.context.getProfile() and self.context.getProfile().getProfileTitle() or '';

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

class AnalysisRequestAddView(AnalysisRequestViewView):
    """ The main AR Add form
    """
    template = ViewPageTemplateFile("templates/analysisrequest_edit.pt")

    def __init__(self, context, request):
        super(AnalysisRequestAddView, self).__init__(context, request)
        self.col_count = 4
        self.came_from = "add"
        self.DryMatterService = self.context.bika_settings.getDryMatterService()

    def __call__(self):
        return self.template()

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
        for analysis in pc(portal_type = "Analysis",
                           getRequestID = self.context.RequestID):
            analysis = analysis.getObject()
            service = analysis.getService()
            res.append([service.getPointOfCapture(),
                        service.getCategoryUID(),
                        service.UID()])
        return res

class AnalysisRequestManageResultsView(AnalysisRequestViewView):
    template = ViewPageTemplateFile("templates/analysisrequest_manage_results.pt")

    def __call__(self):
        wf_tool = getToolByName(self.context, 'portal_workflow')
        pc = getToolByName(self.context, 'portal_catalog')
        self.Field = AnalysesView(self.context, self.request,
                                  getPointOfCapture = 'field').contents_table()
        self.Lab = AnalysesView(self.context, self.request,
                                getPointOfCapture = 'lab').contents_table()

        form = self.request.form
        if form.has_key("submitted"):
            import pprint
            pprint.pprint(form)

        return self.template()


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
        #XXXplone.protect.CheckAuthenticator(self.request)
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
            if items[x]['uid'] in self.request.get('hide_uids', ''): continue
            if items[x]['uid'] in self.request.get('selected_uids', ''):
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
    pagesize = 25

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
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            if items[x]['uid'] in self.request.get('hide_uids', ''): continue
            if items[x]['uid'] in self.request.get('selected_uids', ''):
                items[x]['checked'] = True
            items[x]['view_url'] = obj.absolute_url() + "/view"
            items[x]['SampleType'] = obj.getSampleType().Title()
            items[x]['SamplePoint'] = obj.getSamplePoint() and obj.getSamplePoint().Title()
            items[x]['getDateReceived'] = obj.getDateReceived() and \
                 self.context.toLocalizedTime(obj.getDateReceived(), long_format = 0) or ''
            items[x]['getDateSampled'] = obj.getDateSampled() and \
                 self.context.toLocalizedTime(obj.getDateSampled(), long_format = 0) or ''
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

def getServiceDependencies(context, service_uid):
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
        for service_uid, service_deps in deps.items():
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

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        result = getServiceDependencies(self.context, self.request.get('uid', ''))
        if (not result) or (len(result.keys()) == 0):
            result = None
        return json.dumps(result)

class AJAXExpandCategory(BikaListingView):
    """ AJAX requests pull this view for insertion when category header rows are clicked/expanded. """
    template = ViewPageTemplateFile("templates/analysisrequest_analysisservices.pt")

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)
        if hasattr(self.context, 'getRequestID'): self.came_from = "edit"
        return self.template()

    def Services(self, poc, CategoryUID):
        """ return a list of services brains """
        pc = getToolByName(self.context, 'portal_catalog')
        services = pc(portal_type = "AnalysisService", getPointOfCapture = poc, getCategoryUID = CategoryUID)
        return services

class AJAXProfileServices(BrowserView):
    """ AJAX requests pull this to retrieve a list of services in an AR Profile.
        return JSON data {poc_categoryUID: [serviceUID,serviceUID], ...}
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        rc = getToolByName(self, 'reference_catalog')
        pc = getToolByName(self, 'portal_catalog')

        profile = rc.lookupObject(self.request['profileUID'])
        if not profile: return

        services = {}
        for service in profile.getService():
            service = pc(portal_type = "AnalysisService", UID = service.UID())[0]
            categoryUID = service.getCategoryUID
            poc = service.getPointOfCapture
            try: services["%s_%s" % (poc, categoryUID)].append(service.UID)
            except: services["%s_%s" % (poc, categoryUID)] = [service.UID, ]

        return json.dumps(services)

def getBackReferences(context, service_uid):
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
    walk([service, ])

    return services

class AJAXgetBackReferences():
    """ Return json(getBackReferences) """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        result = getBackReferences(self.context, self.request.get('uid', ''))
        if (not result) or (len(result) == 0):
            result = []
        return json.dumps([r.UID() for r in result])

class AJAXAnalysisRequestSubmit():

    def __init__(self, context, request):
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
                    error_key = " column: %s: %s" % (int(column) + 1, field or '')
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
                    ARs.append(ar_id)
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

                ar.setAnalyses(Analyses, prices = prices)

                if (values.has_key('profileTitle')):
                    profile_id = self.context.generateUniqueId('ARProfile')
                    self.context.invokeFactory(id = profile_id, type_name = 'ARProfile')
                    profile = self.context[profile_id]
                    ar.edit(Profile = profile)
                    profile.setProfileTitle(values['profileTitle'])
                    analyses = ar.getAnalyses()
                    services_array = []
                    for a in analyses:
                        services_array.append(a.getService().UID())
                    profile.setService(services_array)
                    profile.reindexObject()

                if values.has_key('SampleID') and wftool.getInfoFor(sample, 'review_state') != 'due':
                    wftool.doActionFor(ar, 'receive')

            ar.setAnalyses(Analyses, prices = prices)

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

class AJAXAnalysisRequestSubmitResults(AnalysisRequestViewView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)

        if form.has_key("save_button") and self.request.form.has_key("Results"):
            wf = getToolByName(self.context, 'portal_workflow')
            pc = getToolByName(self.context, 'portal_catalog')
            rc = getToolByName(self.context, 'reference_catalog')

            for analysis_uid, result in self.request.form['Results'][0].items():
                analysis = rc.lookupObject(analysis_uid)
                service = analysis.getService()

                uncertainty = None
                service = analysis.getService()

                if result:
                    precision = service.getPrecision()
                    options = service.getResultOptions()
                    try:
                        if precision:
                            result = "%%.%df"%precision % float(result)
                    except:
                        if options:
                            pass

                analysis.edit(
                    Result = result,
                    InterimFields = json.loads(form["InterimFields"][0][analysis_uid]),
                    Retested = form.has_key('retested') and form['retested'].has_key(analysis_uid),
                    Unit = service.getUnit()
                )

#             XXX   wf.doActionFor(analysis, 'submit')

            if self.context.getReportDryMatter():
                self.context.setDryMatterResults()

            message = "Changes saved."
        else:
            message = "Changes Cancelled."

        self.context.plone_utils.addPortalMessage(message, 'info')
        return json.dumps({'success':message})

class AnalysisRequestsView(BikaListingView):
    """ The main portal Analysis Requests action tab
    """
    title = "AnalysisRequests"
    description = ""
    show_editable_border = False
    contentFilter = {'portal_type':'AnalysisRequest', 'path':{"query": ["/"], "level" : 0 }}

    columns = {
           'getRequestID': {'title': _('Request ID')},
           'Client': {'title': _('Client')},
           'getClientOrderNumber': {'title': _('Client Order')},
           'getClientReference': {'title': _('Client Ref')},
           'getClientSampleID': {'title': _('Client Sample')},
           'getSampleTypeTitle': {'title': _('Sample Type')},
           'getSamplePointTitle': {'title': _('Sample Point')},
           'getDateReceived': {'title': _('Date Received')},
           'getDatePublished': {'title': _('Date Published')},
           'state_title': {'title': _('State'), },
    }

    review_states = [
                {'title': _('All'), 'id':'all',
                 'columns':['getRequestID',
                            'Client',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived',
                            'getDatePublished',
                            'state_title']},
                {'title': _('Sample due'), 'id':'sample_due',
                 'transitions': ['cancel', 'receive'],
                 'columns':['getRequestID',
                            'Client',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle']},
                {'title': _('Sample received'), 'id':'sample_received',
                 'transitions': ['cancel'],
                 'columns':['getRequestID',
                            'Client',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived']},
                {'title': _('Assigned to Worksheet'), 'id':'assigned',
                 'transitions': ['cancel'],
                 'columns':['getRequestID',
                            'Client',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived']},
                {'title': _('To be verified'), 'id':'to_be_verified',
                 'transitions': ['cancel', 'verify'],
                 'columns':['getRequestID',
                            'Client',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived']},
                {'title': _('Verified'), 'id':'verified',
                 'transitions': ['cancel', 'publish'],
                 'columns':['getRequestID',
                            'Client',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived']},
                {'title': _('Published'), 'id':'published',
                 'columns':['getRequestID',
                            'Client',
                            'getClientOrderNumber',
                            'getClientReference',
                            'getClientSampleID',
                            'getSampleTypeTitle',
                            'getSamplePointTitle',
                            'getDateReceived',
                            'getDatePublished']},
                ]

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.Title(), _("Analysis Requests"))
        self.description = ""

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for i, item in enumerate(items):
            if not item.has_key('obj'): continue
            obj = item['obj']
            items[i]['getDateReceived'] = item['getDateReceived'] and \
                self.context.toLocalizedTime(item['getDateReceived'], long_format = 0) or ''
            items[i]['Client'] = obj.getObject().aq_parent.Title()
            items[i]['links'] = {'getRequestID': item['url']}
        return items
