from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView, WorkflowAction
from bika.lims.browser.client import ClientAnalysisRequestsView
from bika.lims.browser.publish import Publish
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.utils import isActive, TimeOrDate
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.component import getMultiAdapter
from zope.interface import implements, alsoProvides
from bika.lims import EditResults, EditAR, ManageResults, ResultsNotRequested
import json
import plone
import transaction
import urllib

class AnalysisRequestWorkflowAction(WorkflowAction):
    """ Workflow actions taken in AnalysisRequest context
        This function is called to do the worflow actions
        that apply to Analysis objects
    """
    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        skiplist = self.request.get('workflow_skiplist', [])
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        # combine data from multiple bika listing tables.
        # XXX This should be a single hidden field for all tables rendered
        item_data = {}
        if 'item_data' in form:
            if type(form['item_data']) == list:
                for i_d in form['item_data']:
                    for i,d in json.loads(i_d).items():
                        item_data[i] = d
            else:
                item_data = json.loads(form['item_data'])

        ## publish
        if action in ('prepublish', 'publish', 'prepublish'):
            if not isActive(self.context):
                message = _('Item is inactive.')
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.request.response.redirect(self.context.absolute_url())
                return

            # XXX publish entire AR.
            transitioned = Publish(self.context,
                                   self.request,
                                   action,
                                   [self.context, ])()
            if len(transitioned) == 1:
                message = _('message_item_published',
                    default = '${items} was published.',
                    mapping = {'items': ', '.join(transitioned)})
            else:
                message = _('No ARs were published.')
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        ## submit
        elif action == 'submit' and self.request.form.has_key("Result"):
            if not isActive(self.context):
                message = _('Item is inactive.')
                self.context.plone_utils.addPortalMessage(message, 'info')
                self.request.response.redirect(self.context.absolute_url())
                return

            selected_analyses = WorkflowAction._get_selected_items(self)
            results = {}
            hasInterims = {}

            # first save results for entire form
            for uid, result in self.request.form['Result'][0].items():
                if uid in selected_analyses:
                    analysis = selected_analyses[uid]
                else:
                    analysis = rc.lookupObject(uid)
                if not analysis:
                    # ignore result if analysis object no longer exists
                    continue
                if not(getSecurityManager().checkPermission(EditResults, analysis)):
                    # or changes no longer allowed
                    continue
                results[uid] = result
                service = analysis.getService()
                interimFields = item_data[uid]
                if len(interimFields) > 0:
                    hasInterims[uid] = True
                else:
                    hasInterims[uid] = False
                unit = service.getUnit()
                analysis.edit(
                    Result = result,
                    InterimFields = interimFields,
                    Retested = form.has_key('retested') and \
                               form['retested'].has_key(uid),
                    Unit = unit and unit or '')

            # discover which items may be submitted
            submissable = []
            for uid, analysis in selected_analyses.items():
                if uid not in results:
                    continue
                if not results[uid]:
                    continue
                can_submit = True
                for dependency in analysis.getDependencies():
                    dep_state = workflow.getInfoFor(dependency, 'review_state')
                    if hasInterims[uid]:
                        if dep_state in ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
                            can_submit = False
                            break
                    else:
                        if dep_state in ('sample_due', 'sample_received',):
                            can_submit = False
                            break
                if can_submit and analysis not in submissable:
                    submissable.append(analysis)

            # and then submit them.
            for analysis in submissable:
                if not analysis.UID() in skiplist:
                    try:
                        workflow.doActionFor(analysis, 'submit')
                    except WorkflowException:
                        pass

            if self.context.getReportDryMatter():
                self.context.setDryMatterResults()

            message = _("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        ## verify
        elif action == 'verify':
            # default bika_listing.py/WorkflowAction, but then go to view screen.
            self.destination_url = self.context.absolute_url()
            WorkflowAction.__call__(self)

        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

class AnalysisRequestViewView(BrowserView):
    """ AR View form
        The AR fields are printed in a table, using analysisrequest_view.py
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")

    def __init__(self, context, request):
        super(AnalysisRequestViewView, self).__init__(context, request)

        plone_layout = getMultiAdapter((context, request), name = u'plone_layout')
        #self.view_url = self.absolute_url()
        self.icon = "++resource++bika.lims.images/analysisrequest_big.png"
        self.TimeOrDate = TimeOrDate

    def __call__(self):
        ar = self.context
        self.tables = {}
        for poc in POINTS_OF_CAPTURE:
            if self.context.getAnalyses(getPointOfCapture=poc):
                t = AnalysesView(ar,
                                 self.request,
                                 getPointOfCapture = poc)
                t.allow_edit = False
                t.show_select_column = False
                self.tables[POINTS_OF_CAPTURE.getValue(poc)] = t.contents_table()
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
        for proxy in pc(portal_type = 'ARProfile',
                        getClientUID = self.context.UID(),
                        inactive_state = 'active',
                        sort_on = 'sortable_title'):
                profiles.append((proxy.Title, proxy.getObject()))
        for proxy in pc(portal_type = 'ARProfile',
                        getClientUID = self.context.bika_setup.bika_arprofiles.UID(),
                        inactive_state = 'active',
                        sort_on = 'sortable_title'):
                profiles.append((_('Lab:') + proxy.Title, proxy.getObject()))
        return profiles

    def SelectedServices(self):
        """ return information about services currently selected in the
            context AR.
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

    def Categories(self):
        """ Dictionary keys: poc
            Dictionary values: (Category UID,category Title)
        """
        pc = getToolByName(self.context, 'portal_catalog')
        cats = {}
        for service in pc(portal_type = "AnalysisService",
                          inactive_state = 'active'):
            service = service.getObject()
            poc = service.getPointOfCapture()
            if not cats.has_key(poc): cats[poc] = []
            category = service.getCategory()
            cat = (category.UID(), category.Title())
            if cat not in cats[poc]:
                cats[poc].append(cat)
        return cats

    def getDefaultSpec(self):
        """ Returns 'lab' or 'client' to set the initial value of the
            specification radios
        """
        mt = getToolByName(self.context, 'portal_membership')
        pg = getToolByName(self.context, 'portal_groups')
        member = mt.getAuthenticatedMember();
        member_groups = [pg.getGroupById(group.id).getGroupName() \
                         for group in pg.getGroupsByUserId(member.id)]
        default_spec = ('Clients' in member_groups) and 'client' or 'lab'
        return default_spec

    def getHazardous(self):
        return self.context.getSample().getSampleType().getHazardous()

    def getARProfileTitle(self):
        return self.context.getProfile() and \
               self.context.getProfile().Title() or '';

    def get_requested_analyses(self):
        ##
        ##title=Get requested analyses
        ##
        result = []
        cats = {}
        for analysis in self.context.getAnalyses(full_objects = True):
            if analysis.review_state == 'not_requested':
                continue
            service = analysis.getService()
            category_name = service.getCategoryName()
            if not category_name in cats:
                cats[category_name] = {}
            cats[category_name][analysis.Title()] = analysis

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

        result = []
        for analysis in self.context.getAnalyses():
            if analysis.review_state == 'not_requested':
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
        actions_tool = self.context.portal_actions

        actions = {}
        for analysis in self.context.getAnalyses():
            if analysis.review_state in \
               ('not_requested', 'to_be_verified', 'verified'):
                analysis = analysis.getObject()
                a = actions_tool.listFilteredActionsFor(analysis)
                for action in a['workflow']:
                    if actions.has_key(action['id']):
                        continue
                    actions[action['id']] = action

        return actions.values()


class AnalysisRequestAddView(AnalysisRequestViewView):
    """ The main AR Add form
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_edit.pt")

    def __init__(self, context, request):
        AnalysisRequestViewView.__init__(self, context, request)
        self.came_from = "add"
        self.can_edit_sample = True
        self.can_edit_ar = True
        self.DryMatterService = self.context.bika_setup.getDryMatterService()
        request.set('disable_plone.rightcolumn',1);

        self.col_count = 6

    def __call__(self):
        return self.template()

class AnalysisRequestEditView(AnalysisRequestAddView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_edit.pt")

    def __init__(self, context, request):
        super(AnalysisRequestEditView, self).__init__(context, request)
        self.col_count = 1
        self.came_from = "edit"

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')

        if workflow.getInfoFor(ar, 'cancellation_state') == "cancelled":
            self.request.response.redirect(ar.absolute_url())
        elif not(getSecurityManager().checkPermission(EditAR, ar)):
            self.request.response.redirect(ar.absolute_url())
        else:
            can_edit_sample = True
            can_edit_ar = True
            for a in ar.getAnalyses():
                if workflow.getInfoFor(a.getObject(), 'review_state') in ('verified', 'published'):
                    can_edit_sample = False
                    can_edit_ar = False
                    break
            if can_edit_sample:
                sample = ar.getSample()
                if workflow.getInfoFor(sample, 'cancellation_state') == "cancelled":
                # Redundant check. If sample is cancelled then AR is too (in theory).
                    can_edit_sample = False
                else:
                    sars = sample.getAnalysisRequests()
                    for sar in sars:
                        if sar != ar:
                            for a in sar.getAnalyses():
                                if workflow.getInfoFor(a.getObject(), 'review_state') in ('verified', 'published'):
                                    can_edit_sample = False
                                    break
                            if not can_edit_sample:
                                break
            self.can_edit_sample = can_edit_sample
            self.can_edit_ar = can_edit_ar
            return self.template()

    def getARProfileUID(self):
        return self.context.getProfile() and \
               self.context.getProfile().UID() or '';

class AnalysisRequestManageResultsView(AnalysisRequestViewView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_manage_results.pt")

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')

        if workflow.getInfoFor(ar, 'cancellation_state') == "cancelled":
            self.request.response.redirect(ar.absolute_url())
        elif not(getSecurityManager().checkPermission(ManageResults, ar)):
            self.request.response.redirect(ar.absolute_url())
        else:
            self.tables = {}
            for poc in POINTS_OF_CAPTURE:
                if self.context.getAnalyses(getPointOfCapture=poc):
                    t = AnalysesView(ar,
                                     self.request,
                                     getPointOfCapture = poc)
                    t.allow_edit = True
                    t.review_states[0]['transitions'] = ['submit', 'retract', 'verify']
                    t.show_select_column = True
                    self.tables[POINTS_OF_CAPTURE.getValue(poc)] = t.contents_table()
            return self.template()

class AnalysisRequestResultsNotRequestedView(AnalysisRequestManageResultsView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/analysisrequest_analyses_not_requested.pt")

    def __call__(self):
        ar = self.context
        workflow = getToolByName(ar, 'portal_workflow')

        if workflow.getInfoFor(ar, 'cancellation_state') == "cancelled":
            self.request.response.redirect(ar.absolute_url())
        elif not(getSecurityManager().checkPermission(ResultsNotRequested, ar)):
            self.request.response.redirect(ar.absolute_url())
        else:
            return self.template()

class AnalysisRequestContactCCs(BrowserView):
    """ Returns lists of UID/Title for preconfigured CC contacts
        When a client contact is selected from the #contact dropdown,
        the dropdown's ccuids attribute is set to the Contact UIDS
        returned here, and the #cc_titles textbox is filled with Contact Titles
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request.form)
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        uid = self.request.form.keys() and self.request.form.keys()[0] or None
        if not uid:
            return
        contact = rc.lookupObject(uid)
        cc_uids = []
        cc_titles = []
        for cc in contact.getCCContact():
            active = isActive(contact)
            if not active:
                continue
            cc_uids.append(cc.UID())
            cc_titles.append(cc.Title())
        return json.dumps([",".join(cc_uids),
                           ",".join(cc_titles)])

class AnalysisRequestSelectCCView(BikaListingView):

    template = ViewPageTemplateFile("templates/analysisrequest_select_cc.pt")

    def __init__(self, context, request):
        super(AnalysisRequestSelectCCView, self).__init__(context, request)
        self.title = _("Contacts to CC")
        self.description = _("Select the contacts that will receive analysis results for this request.")
        self.contentFilter = {'portal_type': 'Contact',
                              'sort_on':'sortable_title',
                              'inactive_state': 'active'}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_workflow_action_buttons = False
        self.show_select_column = True
        self.pagesize = 25

        request.set('disable_border', 1)

        self.columns = {
            'getFullname': {'title': _('Full Name')},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone'],
             },
        ]

    def folderitems(self):
        old_items = BikaListingView.folderitems(self)
        items = []
        for x, item in enumerate(old_items):
            if not item.has_key('obj'):
                items.append(item)
                continue
            obj = item['obj']
            if obj.UID() in self.request.get('hide_uids', ()):
                continue
            item['getFullname'] = obj.getFullname()
            item['getEmailAddress'] = obj.getEmailAddress()
            item['getBusinessPhone'] = obj.getBusinessPhone()
            item['getMobilePhone'] = obj.getMobilePhone()
            if self.request.get('selected_uids', '').find(item['uid']) > -1:
                item['selected'] = True
            items.append(item)
        return items

class AnalysisRequestSelectSampleView(BikaListingView):

    template = ViewPageTemplateFile("templates/analysisrequest_select_sample.pt")

    def __init__(self, context, request):
        super(AnalysisRequestSelectSampleView, self).__init__(context, request)
        self.title = _("Select sample")
        self.description = _("Click on a sample to create a secondary AR.")
        self.contentFilter = {'portal_type': 'Sample',
                              'sort_on':'id',
                              'sort_order': 'reverse',
                              'cancellation_state': 'active'}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25

        request.set('disable_border', 1)

        self.columns = {
            'getSampleID': {'title': _('Sample ID')},
            'getClientSampleID': {'title': _('Client SID')},
            'getClientReference': {'title': _('Client Reference')},
            'getSampleTypeTitle': {'title': _('Sample Type')},
            'getSamplePointTitle': {'title': _('Sample Point')},
            'getDateReceived': {'title': _('Date Received')},
            'state_title': {'title': _('State')},
        }

        self.review_states = [
            {'id':'all',
             'title': _('All Samples'),
             'columns': ['getSampleID',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'state_title']},
            {'id':'due',
             'title': _('Sample Due'),
             'contentFilter': {'review_state': 'due'},
             'columns': ['getSampleID',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle']},
            {'id':'received',
             'title': _('Received'),
             'contentFilter': {'review_state': 'received'},
             'columns': ['getSampleID',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getDateReceived']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x, item in enumerate(items):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['class']['getSampleID'] = "select_sample"
            if items[x]['uid'] in self.request.get('hide_uids', ''): continue
            if items[x]['uid'] in self.request.get('selected_uids', ''):
                items[x]['selected'] = True
            items[x]['view_url'] = obj.absolute_url() + "/view"
            items[x]['getClientReference'] = obj.getClientReference()
            items[x]['getClientSampleID'] = obj.getClientSampleID()
            items[x]['getSampleID'] = obj.getSampleID()
            if obj.getSampleType().getHazardous():
                items[x]['after']['getSampleID'] = \
                     "<img src='++resource++bika.lims.images/hazardous.png' title='Hazardous'>"
            items[x]['getSampleTypeTitle'] = obj.getSampleTypeTitle()
            items[x]['getSamplePointTitle'] = obj.getSamplePointTitle()
            items[x]['row_data'] = json.dumps({
                'SampleID': items[x]['title'],
                'ClientReference': items[x]['getClientReference'],
                'Requests': ", ".join([o.Title() for o in obj.getAnalysisRequests()]),
                'ClientSampleID': items[x]['getClientSampleID'],
                'DateReceived': obj.getDateReceived() and \
                               obj.getDateReceived().asdatetime().strftime("%d %b %Y") or '',
                'DateSampled': obj.getDateSampled() and \
                               obj.getDateSampled().asdatetime().strftime("%d %b %Y") or '',
                'SampleType': items[x]['getSampleTypeTitle'],
                'SamplePoint': items[x]['getSamplePointTitle'],
                'Composite': obj.getComposite(),
                'field_analyses': self.FieldAnalyses(obj),
                'column': self.request.get('column', None),
            })
            items[x]['getDateReceived'] = obj.getDateReceived() and \
                 TimeOrDate(self.context, obj.getDateReceived()) or ''
            items[x]['getDateSampled'] = obj.getDateSampled() and \
                 TimeOrDate(self.context, obj.getDateSampled()) or ''
        return items

    def FieldAnalyses(self, sample):
        """ Returns a dictionary of lists reflecting Field Analyses
            linked to this sample (meaning field analyses on this sample's
            first AR. For secondary ARs field analyses and their values are
            read/written from the first AR.)
            {category_uid: [service_uid, service_uid], ... }
        """
        res = {}
        ars = sample.getAnalysisRequests()
        if len(ars) > 0:
            for analysis in ars[0].getAnalyses(full_objects = True):
                service = analysis.getService()
                if service.getPointOfCapture() == 'field':
                    catuid = service.getCategoryUID()
                    if res.has_key(catuid):
                        res[catuid].append(service.UID())
                    else:
                        res[catuid] = [service.UID()]
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
    rc = getToolByName(context, REFERENCE_CATALOG)
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

class ajaxgetServiceDependencies():
    """ Return json(getServiceDependencies) """

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        result = getServiceDependencies(self.context, self.request.get('uid', ''))
        if (not result) or (len(result.keys()) == 0):
            result = None
        return json.dumps(result)

class ajaxExpandCategory(BikaListingView):
    """ ajax requests pull this view for insertion when category header rows are clicked/expanded. """
    template = ViewPageTemplateFile("templates/analysisrequest_analysisservices.pt")

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)
        if hasattr(self.context, 'getRequestID'): self.came_from = "edit"
        return self.template()

    def Services(self, poc, CategoryUID):
        """ return a list of services brains """
        pc = getToolByName(self.context, 'portal_catalog')
        services = pc(portal_type = "AnalysisService",
                      sort_on = 'sortable_title',
                      inactive_state = 'active',
                      getPointOfCapture = poc,
                      getCategoryUID = CategoryUID)
        return services

class ajaxProfileServices(BrowserView):
    """ ajax requests pull this to retrieve a list of services in an AR Profile.
        return JSON data {poc_categoryUID: [serviceUID,serviceUID], ...}
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        rc = getToolByName(self, REFERENCE_CATALOG)
        pc = getToolByName(self, 'portal_catalog')

        profile = rc.lookupObject(self.request['profileUID'])
        if not profile: return

        services = {}
        for service in pc(portal_type = "AnalysisService",
                          inactive_state = "active",
                          UID = [u.UID() for u in profile.getService()]):
            service = service.getObject()
            categoryUID = service.getCategoryUID()
            poc = service.getPointOfCapture()
            try: services["%s_%s" % (poc, categoryUID)].append(service.UID())
            except: services["%s_%s" % (poc, categoryUID)] = [service.UID(), ]

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

class ajaxgetBackReferences():
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

class ajaxAnalysisRequestSubmit():

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(self.request.form)
        plone.protect.PostOnly(self.request.form)

        came_from = form.has_key('came_from') and form['came_from'] or 'add'
        wftool = getToolByName(self.context, 'portal_workflow')
        pc = getToolByName(self.context, 'portal_catalog')

        errors = {}
        def error(field = None, column = None, message = None):
            if not message:
                message = self.context.translate(
                    'message_input_required',
                    default = 'Input is required but no input given.',
                    domain = 'bika')
            if (column or field):
                error_key = " %s.%s" % (int(column) + 1, field or '')
            else:
                error_key = "Form Error"
            errors[error_key] = message


        if came_from == "edit":

            # First figure out what can be updated
            # ------------------------------------

            ar = self.context

            can_edit = True

            if wftool.getInfoFor(ar, 'cancellation_state') == "cancelled":
                can_edit = False
            elif not(getSecurityManager().checkPermission(EditAR, ar)):
                can_edit = False

            if not can_edit:
                # Go back to 'View' screen with message.
                message = _("Changes not allowed.")
                ar.plone_utils.addPortalMessage(message, 'info')
                return json.dumps({'success':message})

            can_edit_sample = True
            can_edit_ar = True

            for a in ar.getAnalyses():
                if wftool.getInfoFor(a.getObject(), 'review_state') in ('verified', 'published'):
                    can_edit_sample = False
                    can_edit_ar = False
                    break

            if can_edit_sample:
                sample = ar.getSample()
                if wftool.getInfoFor(sample, 'cancellation_state') == "cancelled":
                # Redundant check. If sample is cancelled then AR is too (in theory).
                    can_edit_sample = False
                else:
                    sars = sample.getAnalysisRequests()
                    for sar in sars:
                        if sar != ar:
                            for a in sar.getAnalyses():
                                if wftool.getInfoFor(a.getObject(), 'review_state') in ('verified', 'published'):
                                    can_edit_sample = False
                                    break
                            if not can_edit_sample:
                                break


            # Now see what's on the form and validate it
            # ------------------------------------------

            values = form["ar.0"].copy()

            # Validate sample info (if there is any)
            if can_edit_sample:
                if not form['can_edit_sample']:
                    # Was greyed-out on the screen.
                    can_edit_sample = False

            if can_edit_sample:
                required_fields = ['SampleType', 'DateSampled']
                for field in required_fields:
                    if not values.has_key(field):
                        error(field, 0)
                validated_fields = ('SampleType', 'SamplePoint')
                for field in validated_fields:
                    # ignore empty field values
                    if not values.has_key(field):
                        continue
                    if field == "SampleType":
                        if not pc(portal_type = 'SampleType',
                                  inactive_state = 'active',
                                  Title = values[field]):
                            error(field, 0, '%s is not a valid sample type' % values[field])
                    elif field == "SamplePoint":
                        if not pc(portal_type = 'SamplePoint',
                                  inactive_state = 'active',
                                  Title = values[field]):
                            error(field, 0, '%s is not a valid sample point' % values[field])

            # Check if there is any general AR info
            if can_edit_ar:
                if not form['can_edit_ar']:
                    # Was greyed-out on the screen.
                    can_edit_ar = False

            # Check for analyses
            if not values.has_key("Analyses"):
                error(message = _("No analyses have been selected."))

            if errors:
                return json.dumps({'errors':errors})

            # OK, so there's something to update...
            # -------------------------------------

            Analyses = values['Analyses']
            del values['Analyses']

            if can_edit_sample:
            # update Sample
                sample.edit(
                    ClientReference = values.has_key('ClientReference') and values['ClientReference'] or '',
                    ClientSampleID = values.has_key('ClientSampleID') and values['ClientSampleID'] or '',
                    DateSampled = values.has_key('DateSampled') and values['DateSampled'] or '',
                    SampleType = values.has_key('SampleType') and values['SampleType'] or '',
                    SamplePoint = values.has_key('SamplePoint') and values['SamplePoint'] or '',
                    Composite = values.has_key('Composite') and values['Composite'] or ''
                )
                dis_date = sample.disposal_date()
                sample.setDisposalDate(dis_date)

            if can_edit_ar:
            # update general AR info
                ar.edit(
                    Contact = form['Contact'],
                    CCContact = form['cc_uids'].split(","),
                    CCEmails = form['CCEmails'],
                    ClientOrderNumber = values.has_key('ClientOrderNumber') and values['ClientOrderNumber'] or ''
                )

            # update Analyses and related info
            setProfile = False
            if not (values.has_key('ARProfile') and values['ARProfile'] != ""):
                # Profile may have been cleared due to addition/removal of analyses.
                # Note: User is not allowed to select a profile on the edit screen.
                setProfile = True
                profile = None
            if values.has_key('profileTitle'):
                # User wants to save a new profile.
                client = ar.aq_parent
                profile_id = client.generateUniqueId('ARProfile')
                client.invokeFactory(id = profile_id,
                                           type_name = 'ARProfile')
                profile = client[profile_id]
                profile.edit(title = values['profileTitle'],
                             Service = Analyses)
                profile.processForm()
                setProfile = True

            if values.has_key('ReportDryMatter'):
                reportDryMatter = True
            else:
                reportDryMatter = False

            if values.has_key('InvoiceExclude'):
                invoiceExclude = True
            else:
                invoiceExclude = False

            if setProfile:
                ar.edit(
                    ReportDryMatter = reportDryMatter,
                    InvoiceExclude = invoiceExclude,
                    Profile = profile
                )
            else:
                ar.edit(
                    ReportDryMatter = reportDryMatter,
                    InvoiceExclude = invoiceExclude
                )

            prices = form['Prices']
            ar.setAnalyses(Analyses, prices = prices)

            message = _("Changes Saved.")


        else:
        # came_from == "add"
        # ------------------

            # First make a list of non-empty columns
            columns = []
            for column in range(int(form['col_count'])):
                formkey = "ar.%s" % column
                # first time in, unused columns not in form
                if not form.has_key(formkey):
                    continue
                ar = form[formkey]
                if len(ar.keys()) == 3: # three empty price fields
                    if ar.has_key('subtotal'):
                        continue
                columns.append(column)

            if len(columns) == 0:
                error(message = _("No data was entered."))
                return json.dumps({'errors':errors})

            # Now some basic validation
            required_fields = ['SampleType', 'DateSampled']
            validated_fields = ('SampleID', 'SampleType', 'SamplePoint')

            for column in columns:
                formkey = "ar.%s" % column
                ar = form[formkey]
                if not ar.has_key("Analyses"):
                    error('Analyses', column, _("No analyses have been selected."))

                # check that required fields have values
                for field in required_fields:
                    if not ar.has_key(field):
                        error(field, column)

                # validate field values
                for field in validated_fields:
                    # ignore empty field values
                    if not ar.has_key(field):
                        continue

                    if field == "SampleID":
                        if not pc(portal_type = 'Sample',
                                  cancellation_state = 'active',
                                  id = ar[field]):
                            error(field, column,
                                  '%s is not a valid sample ID' % ar[field])

                    elif field == "SampleType":
                        if not pc(portal_type = 'SampleType',
                                  inactive_state = 'active',
                                  Title = ar[field]):
                            error(field, column,
                                  '%s is not a valid sample type' % ar[field])

                    elif field == "SamplePoint":
                        if not pc(portal_type = 'SamplePoint',
                                  inactive_state = 'active',
                                  Title = ar[field]):
                            error(field, column,
                                  '%s is not a valid sample point' % ar[field])

            if errors:
                return json.dumps({'errors':errors})

            prices = form['Prices']
            ARs = []

            # The actual submission
            for column in columns:
                formkey = "ar.%s" % column
                values = form[formkey].copy()
                ar_number = 1
                profile = None
                if (values.has_key('ARProfile')):
                    profileUID = values['ARProfile']
                    for proxy in pc(portal_type = 'ARProfile',
                                    inactive_state = 'active',
                                    UID = profileUID):
                        profile = proxy.getObject()

                if values.has_key('SampleID'):
                    # Secondary AR
                    sample_id = values['SampleID']
                    sample_proxy = pc(portal_type = 'Sample',
                                      cancellation_state = 'active',
                                      id = sample_id)
                    assert len(sample_proxy) == 1
                    sample = sample_proxy[0].getObject()
                    ar_number = sample.getLastARNumber() + 1
                    sample.edit(LastARNumber = ar_number,
                                Composite = 'Composite' in values and values['Composite'] or False)
                    sample.reindexObject()
                else:
                    # Primary AR
                    sample_id = self.context.generateUniqueId('Sample')
                    self.context.invokeFactory(id = sample_id,
                                               type_name = 'Sample')
                    sample = self.context[sample_id]
                    sample.edit(
                        SampleID = sample_id,
                        LastARNumber = ar_number,
                        DateSubmitted = DateTime(),
                        SubmittedByUser = sample.current_user(),
                        **dict(values)
                    )
                    sample.processForm()
                    dis_date = sample.disposal_date()
                    sample.setDisposalDate(dis_date)
                sample_uid = sample.UID()

                # create the AR

                Analyses = values['Analyses']
                del values['Analyses']

                ar_id = self.context.generateARUniqueId('AnalysisRequest',
                                                        sample_id,
                                                        ar_number)
                self.context.invokeFactory(id = ar_id,
                                           type_name = 'AnalysisRequest')
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
                ar.processForm()
                ARs.append(ar_id)

                ar.setAnalyses(Analyses, prices = prices)

                if (values.has_key('profileTitle')):
                    profile_id = self.context.generateUniqueId('ARProfile')
                    self.context.invokeFactory(id = profile_id,
                                               type_name = 'ARProfile')
                    profile = self.context[profile_id]
                    profile.edit(title = values['profileTitle'],
                                 Service = Analyses)
                    profile.processForm()
                    ar.edit(Profile = profile)

                if values.has_key('SampleID') and \
                   wftool.getInfoFor(sample, 'review_state') != 'due':
                    wftool.doActionFor(ar, 'receive')

            if len(ARs) > 1:
                message = self.context.translate(
                    'message_ars_created',
                    default = 'Analysis requests ${ARs} were successfully created.',
                    mapping = {'ARs': ', '.join(ARs)}, domain = 'bika')
            else:
                message = self.context.translate(
                    'message_ar_created',
                    default = 'Analysis request ${AR} was successfully created.',
                    mapping = {'AR': ', '.join(ARs)}, domain = 'bika')

        self.context.plone_utils.addPortalMessage(message, 'info')
        # automatic label printing
        # won't print labels for Register on Secondary ARs
        new_ars = [ar for ar in ARs if ar.split("-")[-1] == '01']
        if 'register' in self.context.bika_setup.getAutoPrintLabels() and new_ars:
            return json.dumps({'success':message,
                               'labels':new_ars,
                               'labelsize':self.context.bika_setup.getAutoLabelSize()})
        else:
            return json.dumps({'success':message})

class AnalysisRequestsView(ClientAnalysisRequestsView):
    """ The main portal Analysis Requests action tab
    """
    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.title = "%s: %s" % (self.context.aq_parent.Title(), _("Analysis Requests"))
        self.description = ""
        self.content_add_actions = {}
        self.contentFilter = {'portal_type':'AnalysisRequest',
                              'sort_on':'id',
                              'sort_order': 'reverse',
                              'path':{"query": ["/"], "level" : 0 }}
        self.view_url = self.view_url + "/analysisrequests"

        request.set('disable_border', 1)

        self.columns['Client'] = {'title': _('Client')}
        review_states = []
        for review_state in self.review_states:
            review_state['columns'].insert(review_state['columns'].index('getClientOrderNumber'), 'Client')

    def folderitems(self):
        items = super(AnalysisRequestsView, self).folderitems()
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                 (obj.aq_parent.absolute_url(), obj.aq_parent.Title())

        return items
