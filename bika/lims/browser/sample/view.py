from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from bika.lims import PMF
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from bika.lims.utils import getUsers
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements
from . import SampleEdit
import plone
import App


class SampleView(SampleEdit):
    """
    The view of a single sample
    """
    def __call__(self):
        self.allow_edit = False
        return SampleEdit.__call__(self)


class SamplesView(BikaListingView):
    """
    A list of samples view (folder view)
    """
    implements(IViewView)

    def __init__(self, context, request):
        super(SamplesView, self).__init__(context, request)

        request.set('disable_plone.rightcolumn', 1)

        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'Sample',
                              'sort_on':'created',
                              'sort_order': 'reverse',
                              'path': {'query': "/",
                                       'level': 0 }
                              }
        # So far we will only print if the sampling workflow is activated
        if self.context.bika_setup.getSamplingWorkflowEnabled():
            self.context_actions = {
                _('Print sample sheets'): {
                    'url': 'print_sampling_sheets',
                    'icon': '++resource++bika.lims.images/print_32.png'}
                    }
        else:
                self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.allow_edit = True
        self.form_id = "samples"

        if self.view_url.find("/samples") > -1:
            self.request.set('disable_border', 1)
        else:
            self.view_url = self.view_url + "/samples"

        self.icon = self.portal_url + "/++resource++bika.lims.images/sample_big.png"
        self.title = self.context.translate(_("Samples"))
        self.description = ""
        SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        user_is_preserver = 'Preserver' in member.getRoles()
        # Defined in the __init__.py
        self.columns = {
            'getSampleID': {'title': _('Sample ID'),
                            'index':'getSampleID'},
            'Client': {'title': _("Client"),
                       'toggle': True,},
            'Creator': {'title': PMF('Creator'),
                        'index': 'Creator',
                        'toggle': True},
            'Created': {'title': PMF('Date Created'),
                        'index': 'created',
                        'toggle': False},
            'Requests': {'title': _('Requests'),
                         'sortable': False,
                         'toggle': False},
            'getClientReference': {'title': _('Client Ref'),
                                   'index': 'getClientReference',
                                   'toggle': True},
            'getClientSampleID': {'title': _('Client SID'),
                                  'index': 'getClientSampleID',
                                  'toggle': True},
            'getSampleTypeTitle': {'title': _('Sample Type'),
                                   'index': 'getSampleTypeTitle'},
            'getSamplePointTitle': {'title': _('Sample Point'),
                                    'index': 'getSamplePointTitle',
                                    'toggle': False},
            'getStorageLocation': {'title': _('Storage Location'),
                                    'toggle': False},
            'SamplingDeviation': {'title': _('Sampling Deviation'),
                                  'toggle': False},
            'AdHoc': {'title': _('Ad-Hoc'),
                      'toggle': False},
            'getSamplingDate': {'title': _('Sampling Date'),
                                'index':'getSamplingDate',
                                'toggle': True},
            'getDateSampled': {'title': _('Date Sampled'),
                               'index':'getDateSampled',
                               'toggle': SamplingWorkflowEnabled,
                               'input_class': 'datepicker_nofuture',
                               'input_width': '10'},
            'getSampler': {'title': _('Sampler'),
                           'toggle': SamplingWorkflowEnabled},
            'getScheduledSamplingSampler': {
                'title': _('Sampler for scheduled sampling'),
                'toggle': self.context.bika_setup.getScheduleSamplingEnabled()
                },
            'getDatePreserved': {'title': _('Date Preserved'),
                                 'toggle': user_is_preserver,
                                 'input_class': 'datepicker_nofuture',
                                 'input_width': '10'},
            'getPreserver': {'title': _('Preserver'),
                             'toggle': user_is_preserver},
            'DateReceived': {'title': _('Date Received'),
                             'index': 'getDateReceived',
                             'toggle': False},
            'state_title': {'title': _('State'),
                            'index':'review_state'},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'cancellation_state': 'active',
                               'sort_on': 'created'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'DateReceived',
                         'state_title']},
            {'id': 'to_be_sampled',
             'title': _('To be sampled'),
             'contentFilter': {'review_state': ('to_be_sampled',
                                                'scheduled_sampling'),
                               'cancellation_state': 'active',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'columns': ['getSampleID',
                         'Client',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
                         'getSampler',
                         'getPreserver',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'state_title'],
             'transitions': [
                {'id': 'schedule_sampling'}, {'id': 'sample'}],
             },
            {'id': 'sample_due',
             'title': _('Due'),
             'contentFilter': {'review_state': ('to_be_preserved',
                                                'sample_due'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'state_title']},
            {'id': 'sample_received',
             'title': _('Received'),
             'contentFilter': {'review_state':'sample_received',
                              'sort_order': 'reverse',
                              'sort_on':'created'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'DateReceived']},
            {'id':'expired',
             'title': _('Expired'),
             'contentFilter':{'review_state':'expired',
                              'sort_order': 'reverse',
                              'sort_on':'created'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'DateReceived']},
            {'id':'disposed',
             'title': _('Disposed'),
             'contentFilter':{'review_state':'disposed',
                              'sort_order': 'reverse',
                              'sort_on':'created'},
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'getDateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'DateReceived']},
            {'id':'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'sort_order': 'reverse',
                               'sort_on':'created'},
             'transitions': [{'id':'reinstate'}, ],
             'columns': ['getSampleID',
                         'Client',
                         'Creator',
                         'Created',
                         'Requests',
                         'getClientReference',
                         'getClientSampleID',
                         'getSampleTypeTitle',
                         'getSamplePointTitle',
                         'getStorageLocation',
                         'SamplingDeviation',
                         'AdHoc',
                         'getSamplingDate',
                         'getScheduledSamplingSampler',
                         'DateReceived',
                         'getDateSampled',
                         'getSampler',
                         'getDatePreserved',
                         'getPreserver',
                         'state_title']},
        ]

    def folderitems(self, full_objects = False):
        workflow = getToolByName(self.context, "portal_workflow")
        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        translate = self.context.translate
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']

            items[x]['replace']['getSampleID'] = "<a href='%s'>%s</a>" % \
                (items[x]['url'], obj.getSampleID())
            items[x]['replace']['Requests'] = ",".join(
                ["<a href='%s'>%s</a>" % (o.absolute_url(), o.Title())
                 for o in obj.getAnalysisRequests()])
            items[x]['Client'] = obj.aq_parent.Title()
            if hideclientlink == False:
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                    (obj.aq_parent.absolute_url(), obj.aq_parent.Title())
            items[x]['Creator'] = self.user_fullname(obj.Creator())

            items[x]['DateReceived'] = self.ulocalized_time(obj.getDateReceived())

            deviation = obj.getSamplingDeviation()
            items[x]['SamplingDeviation'] = deviation and deviation.Title() or ''

            items[x]['getStorageLocation'] = obj.getStorageLocation() and obj.getStorageLocation().Title() or ''
            items[x]['AdHoc'] = obj.getAdHoc() and True or ''

            items[x]['Created'] = self.ulocalized_time(obj.created())

            samplingdate = obj.getSamplingDate()
            items[x]['getSamplingDate'] = self.ulocalized_time(samplingdate, long_format=1)

            after_icons = ''
            if obj.getSampleType().getHazardous():
                after_icons += "<img title='%s' " \
                    "src='%s/++resource++bika.lims.images/hazardous.png'>" % \
                    (t(_("Hazardous")),
                     self.portal_url)
            if obj.getSamplingDate() > DateTime():
                after_icons += "<img title='%s' " \
                    "src='%s/++resource++bika.lims.images/calendar.png' >" % \
                    (t(_("Future dated sample")),
                     self.portal_url)
            if after_icons:
                items[x]['after']['getSampleID'] = after_icons

            SamplingWorkflowEnabled =\
                self.context.bika_setup.getSamplingWorkflowEnabled()

            if not samplingdate > DateTime() \
                    and SamplingWorkflowEnabled:
                datesampled = self.ulocalized_time(obj.getDateSampled())
                if not datesampled:
                    datesampled = self.ulocalized_time(DateTime())
                    items[x]['class']['getDateSampled'] = 'provisional'
                sampler = obj.getSampler().strip()
                if sampler:
                    items[x]['replace']['getSampler'] = self.user_fullname(sampler)
                if 'Sampler' in member.getRoles() and not sampler:
                    sampler = member.id
                    items[x]['class']['getSampler'] = 'provisional'
            else:
                datesampled = ''
                sampler = ''
            items[x]['getDateSampled'] = datesampled
            items[x]['getSampler'] = sampler
            # sampling workflow - inline edits for Sampler, Date Sampled and
            # Scheduled Sampling Sampler
            checkPermission = self.context.portal_membership.checkPermission
            state = workflow.getInfoFor(obj, 'review_state')
            if state in ['to_be_sampled', 'scheduled_sampling']:
                items[x]['required'] = []
                items[x]['allow_edit'] = []
                items[x]['choices'] = {}
                samplers = getUsers(obj, ['Sampler', 'LabManager', 'Manager'])
                users = [(
                    {'ResultValue': u, 'ResultText': samplers.getValue(u)})
                    for u in samplers]
                # both situations
                if checkPermission(SampleSample, obj) or\
                        self._schedule_sampling_permissions():
                    items[x]['required'].append('getSampler')
                    items[x]['allow_edit'].append('getSampler')
                    items[x]['choices']['getSampler'] = users
                # sampling permissions
                if checkPermission(SampleSample, obj):
                    getAuthenticatedMember = self.context.\
                        portal_membership.getAuthenticatedMember
                    username = getAuthenticatedMember().getUserName()
                    Sampler = sampler and sampler or \
                        (username in samplers.keys() and username) or ''
                    items[x]['required'].append('getDateSampled')
                    items[x]['allow_edit'].append('getDateSampled')
                    items[x]['getSampler'] = Sampler
                # coordinator permissions
                if self._schedule_sampling_permissions():
                    items[x]['required'].append('getSamplingDate')
                    items[x]['allow_edit'].append('getSamplingDate')
                    items[x]['required'].append('getScheduledSamplingSampler')
                    items[x]['allow_edit'].append(
                        'getScheduledSamplingSampler')
                    items[x]['choices']['getScheduledSamplingSampler'] = users
            # These don't exist on samples
            # the columns exist just to set "preserve" transition from lists.
            # XXX This should be a list of preservers...
            items[x]['getPreserver'] = ''
            items[x]['getDatePreserved'] = ''

            # inline edits for Preserver and Date Preserved
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(PreserveSample, obj):
                items[x]['required'] = ['getPreserver', 'getDatePreserved']
                items[x]['allow_edit'] = ['getPreserver', 'getDatePreserved']
                preservers = getUsers(obj, ['Preserver', 'LabManager', 'Manager'])
                getAuthenticatedMember = self.context.portal_membership.getAuthenticatedMember
                username = getAuthenticatedMember().getUserName()
                users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
                         for u in preservers]
                items[x]['choices'] = {'getPreserver': users}
                preserver = username in preservers.keys() and username or ''
                items[x]['getPreserver'] = preserver
                items[x]['getDatePreserved'] = self.ulocalized_time(DateTime())
                items[x]['class']['getPreserver'] = 'provisional'
                items[x]['class']['getDatePreserved'] = 'provisional'

        # Hide Preservation/Sampling workflow actions if the edit columns
        # are not displayed.
        # Hide schedule_sampling if user has no rights
        toggle_cols = self.get_toggle_cols()
        new_states = []
        for i,state in enumerate(self.review_states):
            if state['id'] == self.review_state.get('id', ''):
                if 'getSampler' not in toggle_cols \
                   or 'getDateSampled' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('sample')
                    else:
                        state['hide_transitions'] = ['sample',]
                if 'getPreserver' not in toggle_cols \
                   or 'getDatePreserved' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('preserve')
                    else:
                        state['hide_transitions'] = ['preserve',]
                # Check if the user has the rights to schedule samplings and
                # the check-box 'ScheduleSamplingEnabled' in bikasetup is set
                if self._schedule_sampling_permissions():
                    # Show the workflow transition button 'schedule_sampling'
                    pass
                else:
                    # Hiddes the button
                    state['hide_transitions'] = ['schedule_sampling', ]
            new_states.append(state)
        self.review_states = new_states

        return items

    def _schedule_sampling_permissions(self):
        """
        This function checks if all the 'schedule a sampling' conditions
        are met
        """
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        return self.context.bika_setup.getScheduleSamplingEnabled() and\
            ('SamplingCoordinator' in roles or 'Manager' in roles)
