from AccessControl import getSecurityManager
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import EditSample
from bika.lims import PMF
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.permissions import ManageSamples
from bika.lims.permissions import SampleSample
from bika.lims.permissions import EditResults
from bika.lims.permissions import EditFieldResults
from bika.lims.utils import TimeOrDate
from bika.lims.utils import getUsers
from bika.lims.utils import pretty_user_name_or_id
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import plone

class SampleWorkflowAction(WorkflowAction):
    """ This function is called to do sample workflow transitions, when
        they are invoked from the bika_listing_folder or the plone UI.
    """

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        translate = self.context.translation_service.translate
        skiplist = self.request.get('workflow_skiplist', [])
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if action == "sampled":
            objects = WorkflowAction._get_selected_items(self)
            transitioned = {'to_be_preserved':[], 'sample_due':[]}
            for obj_uid, obj in objects.items():
                # can't transition inactive items
                if workflow.getInfoFor(obj, 'inactive_state', '') == 'inactive':
                    continue

                # grab this object's Sampler and DateSampled from the form
                Sampler = form['getSampler'][0][obj_uid].strip()
                DateSampled = form['getDateSampled'][0][obj_uid].strip()

                # write them to the sample
                obj.edit(Sampler = Sampler and Sampler or '',
                         DateSampled = DateSampled and DateTime(DateSampled) or '')

                # transition the object if both values are present
                if Sampler and DateSampled:
                    workflow.doActionFor(obj, 'sampled')
                    new_state = workflow.getInfoFor(obj, 'review_state')
                    transitioned[new_state].append(obj.Title())

            message = None
            for state in transitioned:
                t = transitioned[state]
                if len(t) > 1:
                    if state == 'to_be_preserved':
                        message = _('${items} are waiting for preservation.',
                                    mapping = {'items': ', '.join(t)})
                    else:
                        message = _('${items} are waiting to be received.',
                                    mapping = {'items': ', '.join(t)})
                    message = self.context.translate(message)
                    self.context.plone_utils.addPortalMessage(message, 'info')
                elif len(t) == 1:
                    if state == 'to_be_preserved':
                        message = _('${item} is waiting for preservation.',
                                    mapping = {'item': ', '.join(t)})
                    else:
                        message = _('${item} is waiting to be received.',
                                    mapping = {'item': ', '.join(t)})
                    message = self.context.translate(message)
                    self.context.plone_utils.addPortalMessage(message, 'info')
            if not message:
                message = _('No changes made.')
                message = self.context.translate(message)
                self.context.plone_utils.addPortalMessage(message, 'info')
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)

        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

class SamplePartitionsView(AnalysesView):

    def selected_cats(self, items):
        return self.categories

    def __init__(self, context, request, **kwargs):
        super(SamplePartitionsView, self).__init__(context, request, **kwargs)
        self.columns['request'] = {'title': _("Analysis Request")}
        self.review_states[0]['columns'].insert(0, "request")

    def folderitems(self, full_objects=True):
        self.contentsMethod = self.context.getAnalyses
        wf = getToolByName(self.context, 'portal_workflow')
        items = super(SamplePartitionsView, self).folderitems()

        self.categories = []
        for x in range(len(items)):

            part = items[x]['obj'].getSamplePartition()
            rs = wf.getInfoFor(part, 'review_state')
            state_title = wf.getTitleForStateOnType(rs, part.portal_type)

            container = part.getContainer()
            container = container and " | %s"%container.Title() or ''
            preservation = part.getPreservation()
            preservation = preservation and " | %s"%preservation.Title() or ''

            cat = "%s%s%s | %s" % \
                (part.id, container, preservation, state_title)
            items[x]['category'] = cat
            if not cat in self.categories:
                self.categories.append(cat)

            ar = items[x]['obj'].aq_parent
            items[x]['request'] = ''
            items[x]['after']['request'] = "<a href='%s'>%s</a>" % \
                (ar.absolute_url(), ar.id)

        return items

class SampleAnalysesView(AnalysesView):
    """ This renders the Field and Lab analyses tables for Samples
    """
    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request)
        for k,v in kwargs.items():
            self.contentFilter[k] = v

    def folderitems(self):
        self.contentsMethod = self.context.getAnalyses
        return AnalysesView.folderitems(self)

class SampleView(BrowserView):
    """ Sample View/Edit form
    """

    implements(IViewView)
    template = ViewPageTemplateFile("templates/sample.pt")
    header_table = ViewPageTemplateFile("templates/header_table.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/sample_big.png"
        self.TimeOrDate = TimeOrDate

    def now(self):
        return DateTime()

    def __call__(self):
        form = self.request.form
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        checkPermission = self.context.portal_membership.checkPermission
        workflow = getToolByName(self.context, 'portal_workflow')
        ars = self.context.getAnalysisRequests()

        props = getToolByName(self.context, 'portal_properties').bika_properties
        sampling_workflow_enabled = props.getProperty('sampling_workflow_enabled')
        datepicker_format = props.getProperty('datepicker_format')

        ## Create header_table data rows
        ar_links = ", ".join(
            ["<a href='%s'>%s</a>"%(ar.absolute_url(), ar.Title())
             for ar in ars])
        sp = self.context.getSamplePoint()
        st = self.context.getSampleType()
        if workflow.getInfoFor(self.context, 'cancellation_state') == "cancelled":
            allow_sample_edit = False
        else:
            edit_states = ['to_be_sampled', 'to_be_preserved', 'sample_due']
            allow_sample_edit = checkPermission(ManageSamples, self.context) \
                and workflow.getInfoFor(self.context, 'review_state') in edit_states
        self.header_rows = [
            {'id': 'ClientReference',
             'title': _('Client Reference'),
             'allow_edit': allow_sample_edit,
             'value': self.context.getClientReference(),
             'type': 'text'},
            {'id': 'ClientSampleID',
             'title': _('Client SID'),
             'allow_edit': allow_sample_edit,
             'value': self.context.getClientSampleID(),
             'type': 'text'},
            {'id': 'Requests',
             'title': _('Requests'),
             'allow_edit': False,
             'value': ar_links,
             'type': 'text'},
            {'id': 'SampleType',
             'title': _('Sample Type'),
             'allow_edit': allow_sample_edit,
             'value': st and st.Title() or '',
             'type': 'text',
             'required': True},
            {'id': 'SamplePoint',
             'title': _('Sample Point'),
             'allow_edit': allow_sample_edit,
             'value': sp and sp.Title() or '',
             'type': 'text'},
            {'id': 'Composite',
             'title': _('Composite'),
             'allow_edit': allow_sample_edit,
             'value': self.context.getComposite(),
             'type': 'boolean'},
            {'id': 'Creator',
             'title': PMF('Creator'),
             'allow_edit': False,
             'value': self.context.Creator(),
             'type': 'text'},
            {'id': 'DateCreated',
             'title': PMF('Date Created'),
             'allow_edit': False,
             'value': self.context.created(),
             'formatted_value': TimeOrDate(self.context,
                                           self.context.created()),
             'type': 'text'},
            {'id': 'SamplingDate',
             'title': _('Sampling Date'),
             'allow_edit': False,
             'value': self.context.getSamplingDate(),
             'formatted_value': TimeOrDate(self.context,
                                           self.context.getSamplingDate()),
             'type': 'text'},
            {'id': 'Sampler',
             'title': _('Sampler'),
             'allow_edit': checkPermission(SampleSample, self.context),
             'value': self.context.getSampler(),
             'formatted_value': pretty_user_name_or_id(self.context,
                                                       self.context.getSampler()),
             'type': 'choices',
             'vocabulary': getUsers(self.context,
                                    ['Sampler', 'LabManager', 'Manager']),
             ##'required': True,
             'condition': sampling_workflow_enabled},
            {'id': 'DateSampled',
             'title': _('Date Sampled'),
             'allow_edit': checkPermission(SampleSample, self.context),
             'value': self.context.getDateSampled().strftime(datepicker_format),
             'formatted_value': TimeOrDate(self.context,
                                           self.context.getDateSampled()),
             'type': 'text',
             'class': 'datepicker',
             ##'required': True,
             'condition': sampling_workflow_enabled},
            {'id': 'DateReceived',
             'title': _('Date Received'),
             'allow_edit': False,
             'value': self.context.getDateReceived(),
             'formatted_value': TimeOrDate(self.context,
                                           self.context.getDateReceived()),
             'type': 'text'},
            {'id': 'DateExpired',
             'title': _('Date Expired'),
             'allow_edit': False,
             'value': self.context.getDateExpired(),
             'formatted_value': TimeOrDate(self.context,
                                           self.context.getDateExpired()),
             'type': 'text'},
            {'id': 'DisposalDate',
             'title': _('Disposal Date'),
             'allow_edit': False,
             'value': self.context.getDisposalDate(),
             'formatted_value': TimeOrDate(self.context,
                                           self.context.getDisposalDate()),
             'type': 'text'},
            {'id': 'DateDisposed',
             'title': _('Date Disposed'),
             'allow_edit': False,
             'value': self.context.getDateDisposed(),
             'formatted_value': TimeOrDate(self.context,
                                           self.context.getDateDisposed()),
             'type': 'text'},
        ]

        if 'header_submitted' in form:
            message = None
            values = {}
            for row in [r for r in self.header_rows if r['allow_edit']]:
                value = form.get(row['id'], '')

                if row.get('required', False) \
                   and row.get('condition', True) \
                   and not value:
                    message = PMF("Input is required but no input given.")
                    break

                if row['id'] == 'SampleType':
                    if not value:
                        message = _('Sample Type is required')
                        break
                    if not bsc(portal_type = 'SampleType', title = value):
                        message = _("${sampletype} is not a valid sample type",
                                    mapping={'sampletype':value})
                        break

                if row['id'] == 'SamplePoint':
                    if value and \
                       not bsc(portal_type = 'SamplePoint', title = value):
                        message = _("${samplepoint} is not a valid sample point",
                                    mapping={'sampletype':value})
                        break

                values[row['id']] = value

            # boolean - checkboxes are present, or not present in form.
            for row in [r for r in self.header_rows
                        if r.get('type', '') == 'boolean']:
                values[row['id']] = row['id'] in form

            if not message:
                self.context.edit(**values)
                self.context.reindexObject()
                ars = self.context.getAnalysisRequests()
                for ar in ars:
                    ar.reindexObject()
                message = PMF("Changes saved.")

            self.context.plone_utils.addPortalMessage(message, 'info')

            self.request.RESPONSE.redirect(self.context.absolute_url())

            ## End of form submit handler

        ## Create Sample Partitions table
        p = SamplePartitionsView(self.context,
                                 self.request,
                                 sort_on = 'getServiceTitle')
        p.allow_edit = True
        p.review_states[0]['transitions'] = [{'id':'submit'},
                                             {'id':'retract'},
                                             {'id':'verify'}]
        p.show_select_column = True
        self.parts = p.contents_table()

        ## Create Field and Lab Analyses tables
        self.tables = {}
        for poc in POINTS_OF_CAPTURE:
            t = SampleAnalysesView(self.context,
                             self.request,
                             getPointOfCapture = poc,
                             sort_on = 'getServiceTitle')
            t.form_id = "sample_%s_analyses" % poc
            if poc == 'field':
                t.allow_edit = EditFieldResults
            else:
                t.allow_edit = EditResults
            t.review_states[0]['transitions'] = [{'id':'submit'},
                                                 {'id':'retract'},
                                                 {'id':'verify'}]
            t.show_select_column = True
            self.tables[POINTS_OF_CAPTURE.getValue(poc)] = t.contents_table()

        return self.template()

    def tabindex(self):
        i = 0
        while True:
            i += 1
            yield i

class SamplesView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Sample',
                              'sort_on':'id',
                              'sort_order': 'reverse',
                              'path': {'query': "/",
                                       'level': 0 }
                              }
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.allow_edit = True

        if self.view_url.find("/samples") > -1:
            self.request.set('disable_border', 1)
        else:
            self.view_url = self.view_url + "/samples"

        self.icon = "++resource++bika.lims.images/sample_big.png"
        self.title = _("Samples")
        self.description = ""

        self.columns = {
            'getSampleID': {'title': _('Sample ID'),
                            'index':'getSampleID'},
            'Client': {'title': _("Client"),
                       'toggle': True,},
            'Requests': {'title': _('Requests'),
                         'sortable': False,
                         'toggle': False},
            'getClientReference': {'title': _('Client Ref'),
                                   'index': 'getClientReference',
                                   'toggle': False},
            'getClientSampleID': {'title': _('Client SID'),
                                  'index': 'getClientSampleID',
                                  'toggle': False},
            'getSampleTypeTitle': {'title': _('Sample Type'),
                                   'index': 'getSampleTypeTitle'},
            'getSamplePointTitle': {'title': _('Sample Point'),
                                    'index': 'getSamplePointTitle',
                                    'toggle': False},
            'getSamplingDate': {'title': _('Sampling Date'),
                                'toggle': True},
            'getDateSampled': {'title': _('Date Sampled'),
                               'toggle': True,
                               'input_class': 'datepicker',
                               'input_width': '10'},
            'getSampler': {'title': _('Sampler'),
                           'toggle': True},
            'DateReceived': {'title': _('Date Received'),
                             'index': 'getDateReceived',
                             'toggle': False},
            'state_title': {'title': _('State'),
                            'index':'review_state'},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'DateReceived',
                         'state_title']},
            {'id':'to_be_sampled',
             'title': _('To Be Sampled'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'getSampleTypeTitle',
                         'getSamplePointTitle']},
            {'id':'to_be_preserved',
             'title': _('To Be Preserved'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'getSampleTypeTitle',
                         'getSamplePointTitle']},
            {'id':'sample_due',
             'title': _('Due'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'getSampleTypeTitle',
                         'getSamplePointTitle']},
            {'id':'sample_received',
             'title': _('Received'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'DateReceived']},
            {'id':'expired',
             'title': _('Expired'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'DateReceived']},
            {'id':'disposed',
             'title': _('Disposed'),
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'DateReceived']},
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled'},
             'transitions': [{'id':'reinstate'}, ],
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getSamplingDate',
                         'DateReceived',
                         'getDateSampled',
                         'getSampler',
                         'state_title']},
        ]

    def folderitems(self, full_objects = False):
        items = BikaListingView.folderitems(self)

        translate = self.context.translation_service.translate

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['replace']['getSampleID'] = "<a href='%s'>%s</a>" % \
                (items[x]['url'], obj.getSampleID())

            requests = ["<a href='%s'>%s</a>" % (o.absolute_url(), o.Title())
                        for o in obj.getAnalysisRequests()]
            items[x]['replace']['Requests'] = ",".join(requests)

            items[x]['Client'] = obj.aq_parent.Title()
            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                (obj.aq_parent.absolute_url(), obj.aq_parent.Title())

            items[x]['DateReceived'] = TimeOrDate(self.context,  obj.getDateReceived())
            items[x]['getDateSampled'] = TimeOrDate(self.context, obj.getDateSampled())

            items[x]['getSampler'] = obj.getSampler().strip()

            items[x]['getSamplingDate'] = TimeOrDate(self.context, obj.getSamplingDate())

            after_icons = ''
            if obj.getSampleType().getHazardous():
                after_icons += "<img title='Hazardous' src='++resource++bika.lims.images/hazardous.png'>"
            if obj.getSamplingDate() > DateTime():
                after_icons += "<img src='++resource++bika.lims.images/calendar.png' title='%s'>" % \
                    translate(_("Future dated sample"))
            if after_icons:
                items[x]['after']['getSampleID'] = after_icons

            # sampling workflow - inline edits for Sampler and Date Sampled
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(SampleSample, obj):
                items[x]['required'] = ['getSampler', 'getDateSampled']
                items[x]['allow_edit'] = ['getSampler', 'getDateSampled']
                users = getUsers(self.context,
                                 ['Sampler', 'LabManager', 'Manager'],
                                 allow_empty=True)
                users = [({'ResultValue': u, 'ResultText': users.getValue(u)})
                         for u in users]
                items[x]['choices'] = {'getSampler': users}
        return items

class ajaxSetDateSampled(BrowserView):
    """ DateSampled is set immediately.
    """

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        value = self.request.get('value', '')
        if not value:
            value = ""
        self.context.setDateSampled(value)
        return "ok"

class ajaxSetSampler(BrowserView):
    """ Sampler is set immediately.
    """

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        plone.protect.CheckAuthenticator(self.request)
        value = self.request.get('value', '')
        if not value:
            value = ""
        if not mtool.getMemberById(value):
            asdf
            return
        self.context.setSampler(value)
        return "ok"