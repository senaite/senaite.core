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
from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.permissions import EditFieldResults
from bika.lims.permissions import EditResults
from bika.lims.permissions import ManageSamples
from bika.lims.permissions import SampleSample
from bika.lims.permissions import PreserveSample
from bika.lims.utils import TimeOrDate
from bika.lims.utils import getUsers
from bika.lims.utils import isActive
from bika.lims.utils import pretty_user_name_or_id
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
import plone
import json

class SamplePartitionsView(BikaListingView):
    def __init__(self, context, request):
        super(SamplePartitionsView, self).__init__(context, request)
        pc = getToolByName(context, 'portal_catalog')
        self.contentsMethod = pc
        self.contentFilter = {'portal_type': 'SamplePartition',
                              'sort_on': 'sortable_title'}
        self.contentFilter['path'] = {"query": "/".join(context.getPhysicalPath()),
                                      "level" : 0 }
        self.context_actions = {}
        self.title = _("Sample Partitions")
        self.icon = "++resource++bika.lims.images/samplepartition_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 1000

        self.columns = {
            'Title': {'title': _('Partition')},
            'getContainer': {'title': _('Container')},
            'getPreservation': {'title': _('Preservation')},
            'getPreserver': {'title': _('Preserver')},
            'getDatePreserved': {'title': _('Date Preserved'),
                                 'input_class': 'datepicker_nofuture',
                                 'input_width': '10'},
            'getDisposalDate': {'title': _('Disposal Date')},
            'state_title': {'title': _('State')},
        }

        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['Title',
                         'getContainer',
                         'getPreservation',
                         'getPreserver',
                         'getDatePreserved',
                         'getDisposalDate',
                         'state_title'],
             'transitions':[{'id': 'preserved'}]},
        ]

    def folderitems(self, full_objects = False):
        workflow = getToolByName(self.context, "portal_workflow")
        items = BikaListingView.folderitems(self)

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            container = obj.getContainer()
            items[x]['getContainer'] = container and container.Title() or ''

            preservation = obj.getPreservation()
            items[x]['getPreservation'] = \
                preservation and preservation.Title() or ''

            datepreserved = obj.getDatePreserved()
            items[x]['getDatePreserved'] = \
                datepreserved and TimeOrDate(self.context, datepreserved) or ''

            disposaldate = obj.getDisposalDate()
            items[x]['getDisposalDate'] = \
                disposaldate and TimeOrDate(self.context, disposaldate) or ''

            preserver = obj.getPreserver().strip()
            items[x]['getPreserver'] = \
                preserver and pretty_user_name_or_id(self.context, preserver) or ''

            # Partition Preservation required
            # inline edits for Preserver and Date Preserved
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(PreserveSample, obj):
                items[x]['required'] = ['getPreserver', 'getDatePreserved']
                items[x]['allow_edit'] = ['getPreserver', 'getDatePreserved']
                preservers = getUsers(obj, ['Preserver', 'LabManager', 'Manager'])
                getAuthenticatedMember = obj.portal_membership.getAuthenticatedMember
                username = getAuthenticatedMember().getUserName()
                users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
                         for u in preservers]
                items[x]['choices'] = {'getPreserver': users}
                items[x]['getPreserver'] = preserver and preserver or \
                    (username in preservers.keys() and username) or ''

        return items

class SampleAnalysesView(AnalysesView):
    """ This renders the Field and Lab analyses tables for Samples
    """
    def __init__(self, context, request, **kwargs):
        AnalysesView.__init__(self, context, request)
        for k,v in kwargs.items():
            self.contentFilter[k] = v
        if kwargs.get('getPointOfCapture', '') == 'lab':
            self.allow_edit = False
            self.columns['Request'] = {'title': _("Request")}
            self.columns['Partition'] = {'title': _("Partition")}
            # Add Request column
            pos = self.review_states[0]['columns'].index('Service') + 1
            self.review_states[0]['columns'].insert(pos, 'Request')
            # Add Partitioncolumn
            self.review_states[0]['columns'].insert(pos, 'Partition')

    def folderitems(self):
        self.contentsMethod = self.context.getAnalyses
        items = AnalysesView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            ar = obj.aq_parent
            items[x]['replace']['Request'] = "<a href='%s'>%s</a>"%(ar.absolute_url(), ar.Title())
            items[x]['Partition'] = obj.getSamplePartition().Title()
        return items

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

    def getDefaultSpec(self):
        """ Returns 'lab' or 'client' to set the initial value of the
            specification radios
        """
        mt = getToolByName(self.context, 'portal_membership')
        pg = getToolByName(self.context, 'portal_groups')
        member = mt.getAuthenticatedMember()
        member_groups = [pg.getGroupById(group.id).getGroupName() \
                         for group in pg.getGroupsByUserId(member.id)]
        default_spec = ('Clients' in member_groups) and 'client' or 'lab'
        return default_spec

    def __call__(self):
        form = self.request.form
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        checkPermission = self.context.portal_membership.checkPermission
        getAuthenticatedMember = self.context.portal_membership.getAuthenticatedMember
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
        samplers = getUsers(self.context, ['Sampler', 'LabManager', 'Manager'], allow_empty=False)
        sampler = self.context.getSampler()
        username = getAuthenticatedMember().getUserName()
        self.header_columns = 3
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
             'value': pretty_user_name_or_id(self.context, self.context.Creator()),
             'type': 'text'},
            {'id': 'DateCreated',
             'title': PMF('Date Created'),
             'allow_edit': False,
             'value': self.context.created(),
             'formatted_value': TimeOrDate(self.context, self.context.created()),
             'type': 'text'},
            {'id': 'SamplingDate',
             'title': _('Sampling Date'),
             'allow_edit': False,
             'value': self.context.getSamplingDate(),
             'formatted_value': TimeOrDate(self.context, self.context.getSamplingDate()),
             'type': 'text'},
            {'id': 'Sampler',
             'title': _('Sampler'),
             'allow_edit': checkPermission(SampleSample, self.context),
             'value': sampler and sampler or (username in samplers.keys() and username) or '',
             'formatted_value': pretty_user_name_or_id(self.context,
                 sampler and sampler or (username in samplers.keys() and username) or ''),
             'type': 'choices',
             'required': True,
             'vocabulary': samplers,
             'condition': sampling_workflow_enabled},
            {'id': 'DateSampled',
             'title': _('Date Sampled'),
             'allow_edit': checkPermission(SampleSample, self.context),
             'value': self.context.getDateSampled() \
                      and self.context.getDateSampled().strftime(datepicker_format) \
                      or '',
             'required': True,
             'formatted_value': TimeOrDate(self.context, self.context.getDateSampled()),
             'type': 'text',
             'class': 'datepicker_nofuture',
             'condition': sampling_workflow_enabled},
            {'id': 'DateReceived',
             'title': _('Date Received'),
             'allow_edit': False,
             'value': self.context.getDateReceived(),
             'formatted_value': TimeOrDate(self.context, self.context.getDateReceived()),
             'type': 'text'},
            {'id': 'DateExpired',
             'title': _('Date Expired'),
             'allow_edit': False,
             'value': self.context.getDateExpired(),
             'formatted_value': TimeOrDate(self.context, self.context.getDateExpired()),
             'type': 'text'},
            {'id': 'DisposalDate',
             'title': _('Disposal Date'),
             'allow_edit': False,
             'value': self.context.getDisposalDate(),
             'formatted_value': TimeOrDate(self.context, self.context.getDisposalDate()),
             'type': 'text'},
            {'id': 'DateDisposed',
             'title': _('Date Disposed'),
             'allow_edit': False,
             'value': self.context.getDateDisposed(),
             'formatted_value': TimeOrDate(self.context, self.context.getDateDisposed()),
             'type': 'text'},
        ]

        if 'header_submitted' in form:
            message = None
            values = {}
            for row in [r for r in self.header_rows if r['allow_edit']]:
                value = form.get(row['id'], '')

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
            for row in [r for r in self.header_rows if r.get('type', '') == 'boolean']:
                values[row['id']] = row['id'] in form

            if not message:
                self.context.edit(**values)
                self.context.reindexObject()
                ars = self.context.getAnalysisRequests()
                for ar in ars:
                    ar.reindexObject()
                message = PMF("Changes saved.")

            if checkPermission(SampleSample, self.context) and \
               values.get('Sampler', '') != '' and \
               values.get('DateSampled', '') != '':
                workflow.doActionFor(self.context, 'sampled')

            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())

            ## End of form submit handler

        ## Create Sample Partitions table
        p = SamplePartitionsView(self.context, self.request)
        p.show_column_toggles = False
        self.parts = p.contents_table()

        ## Create Field and Lab Analyses tables
        self.tables = {}
        for poc in POINTS_OF_CAPTURE:
            if not self.context.getAnalyses({'getPointOfCapture': poc}):
                continue
            t = SampleAnalysesView(self.context,
                             self.request,
                             getPointOfCapture = poc,
                             sort_on = 'getServiceTitle')
            t.form_id = "sample_%s_analyses" % poc
            if poc == 'field':
                t.allow_edit = EditFieldResults
                t.review_states[0]['columns'].remove('DueDate')
            else:
                t.allow_edit = EditResults
            t.show_column_toggles = False
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
            'Creator': {'title': PMF('Creator'),
                                     'index': 'Creator',
                                     'toggle': False},
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
                               'input_class': 'datepicker_nofuture',
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
                         'Creator',
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
                         'Creator',
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
                         'Creator',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getDateSampled',
                         'getSampler',
                         'getSampleTypeTitle',
                         'getSamplePointTitle'],
             'transitions':[{'id':'empty'},]},
            {'id':'sample_due',
             'title': _('Due'),
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
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
                         'Creator',
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
                         'Creator',
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
                         'Creator',
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
                         'Creator',
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

            items[x]['Creator'] = pretty_user_name_or_id(self.context,
                                                         obj.Creator())

            items[x]['DateReceived'] = TimeOrDate(self.context,  obj.getDateReceived())
            items[x]['getDateSampled'] = TimeOrDate(self.context, obj.getDateSampled())

            sampler = obj.getSampler().strip()
            items[x]['getSampler'] = sampler

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
                samplers = getUsers(obj, ['Sampler', 'LabManager', 'Manager'])
                getAuthenticatedMember = self.context.portal_membership.getAuthenticatedMember
                username = getAuthenticatedMember().getUserName()
                users = [({'ResultValue': u, 'ResultText': samplers.getValue(u)})
                         for u in samplers]
                items[x]['choices'] = {'getSampler': users}
                Sampler = sampler and sampler or \
                    (username in samplers.keys() and username) or ''
                items[x]['getSampler'] = pretty_user_name_or_id(self.context,
                                                                Sampler)

        return items
