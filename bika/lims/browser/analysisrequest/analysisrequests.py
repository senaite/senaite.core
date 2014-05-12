from AccessControl import getSecurityManager
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import getUsers
from bika.lims.permissions import *
from bika.lims.utils import to_utf8, getUsers
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


class AnalysisRequestsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)

        request.set('disable_plone.rightcolumn', 1)

        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type': 'AnalysisRequest',
                              'sort_on': 'created',
                              'sort_order': 'reverse',
                              'path': {"query": "/", "level": 0}
                              }

        self.context_actions = {}

        if self.context.portal_type == "AnalysisRequestsFolder":
            self.request.set('disable_border', 1)

        if self.view_url.find("analysisrequests") == -1:
            self.view_url = self.view_url + "/analysisrequests"

        self.allow_edit = True

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.form_id = "analysisrequests"

        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisrequest_big.png"
        self.title = _("Analysis Requests")
        self.description = ""

        SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        user_is_preserver = 'Preserver' in member.getRoles()

        self.columns = {
            'getRequestID': {'title': _('Request ID'),
                             'index': 'getRequestID'},
            'getClientOrderNumber': {'title': _('Client Order'),
                                     'index': 'getClientOrderNumber',
                                     'toggle': True},
            'Creator': {'title': PMF('Creator'),
                                     'index': 'Creator',
                                     'toggle': True},
            'Created': {'title': PMF('Date Created'),
                        'index': 'created',
                        'toggle': False},
            'getSample': {'title': _("Sample"),
                          'toggle': True, },
            'BatchID': {'title': _("Batch ID"), 'toggle': True},
            'SubGroup': {'title': _('Sub-group')},
            'Client': {'title': _('Client'),
                       'toggle': True},
            'getClientReference': {'title': _('Client Ref'),
                                   'index': 'getClientReference',
                                   'toggle': True},
            'getClientSampleID': {'title': _('Client SID'),
                                  'index': 'getClientSampleID',
                                  'toggle': True},
            'ClientContact': {'title': _('Contact'),
                                 'toggle': False},
            'getSampleTypeTitle': {'title': _('Sample Type'),
                                   'index': 'getSampleTypeTitle',
                                   'toggle': True},
            'getSamplePointTitle': {'title': _('Sample Point'),
                                    'index': 'getSamplePointTitle',
                                    'toggle': False},
            'getStorageLocation': {'title': _('Storage Location'),
                                    'toggle': False},
            'SamplingDeviation': {'title': _('Sampling Deviation'),
                                  'toggle': False},
            'Priority': {'title': _('Priority'),
                            'toggle': True,
                            'index': 'Priority',
                            'sortable': True},
            'AdHoc': {'title': _('Ad-Hoc'),
                      'toggle': False},
            'SamplingDate': {'title': _('Sampling Date'),
                             'index': 'getSamplingDate',
                             'toggle': True},
            'getDateSampled': {'title': _('Date Sampled'),
                               'index': 'getDateSampled',
                               'toggle': not SamplingWorkflowEnabled,
                               'input_class': 'datepicker_nofuture',
                               'input_width': '10'},
            'getSampler': {'title': _('Sampler'),
                           'toggle': not SamplingWorkflowEnabled},
            'getDatePreserved': {'title': _('Date Preserved'),
                                 'toggle': user_is_preserver,
                                 'input_class': 'datepicker_nofuture',
                                 'input_width': '10',
                                 'sortable': False},  # no datesort without index
            'getPreserver': {'title': _('Preserver'),
                             'toggle': user_is_preserver},
            'getDateReceived': {'title': _('Date Received'),
                                'index': 'getDateReceived',
                                'toggle': False},
            'getDatePublished': {'title': _('Date Published'),
                                 'index': 'getDatePublished',
                                 'toggle': False},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
            'getProfileTitle': {'title': _('Profile'),
                                'index': 'getProfileTitle',
                                'toggle': False},
            'getTemplateTitle': {'title': _('Template'),
                                 'index': 'getTemplateTitle',
                                 'toggle': False},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'cancellation_state': 'active',
                              'sort_on': 'created',
                              'sort_order': 'reverse'},
             'transitions': [{'id': 'sample'},
                             {'id': 'preserve'},
                             {'id': 'receive'},
                             {'id': 'retract'},
                             {'id': 'verify'},
                             {'id': 'prepublish'},
                             {'id': 'publish'},
                             {'id': 'republish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'ClientContact',
                        'getClientSampleID',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'SamplingDate',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'state_title']},
            {'id': 'sample_due',
             'title': _('Due'),
             'contentFilter': {'review_state': ('to_be_sampled',
                                                'to_be_preserved',
                                                'sample_due'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'sample'},
                             {'id': 'preserve'},
                             {'id': 'receive'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'state_title']},
           {'id': 'sample_received',
             'title': _('Received'),
             'contentFilter': {'review_state': 'sample_received',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'prepublish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived']},
            {'id': 'to_be_verified',
             'title': _('To be verified'),
             'contentFilter': {'review_state': 'to_be_verified',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'retract'},
                             {'id': 'verify'},
                             {'id': 'prepublish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived']},
            {'id': 'verified',
             'title': _('Verified'),
             'contentFilter': {'review_state': 'verified',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'publish'}],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived']},
            {'id': 'published',
             'title': _('Published'),
             'contentFilter': {'review_state': ('published', 'invalid'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'republish'}],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished']},
            {'id': 'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'review_state': ('to_be_sampled', 'to_be_preserved',
                                                'sample_due', 'sample_received',
                                                'to_be_verified', 'attachment_due',
                                                'verified', 'published'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'reinstate'}],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished',
                        'state_title']},
            {'id': 'invalid',
             'title': _('Invalid'),
             'contentFilter': {'review_state': 'invalid',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished']},
            {'id': 'assigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/assigned.png'/>" % (
                       t(_("Assigned")), self.portal_url),
             'contentFilter': {'worksheetanalysis_review_state': 'assigned',
                               'review_state': ('sample_received', 'to_be_verified',
                                                'attachment_due', 'verified',
                                                'published'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'retract'},
                             {'id': 'verify'},
                             {'id': 'prepublish'},
                             {'id': 'publish'},
                             {'id': 'republish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'state_title']},
            {'id': 'unassigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/unassigned.png'/>" % (
                       t(_("Unassigned")), self.portal_url),
             'contentFilter': {'worksheetanalysis_review_state': 'unassigned',
                               'review_state': ('sample_received', 'to_be_verified',
                                                'attachment_due', 'verified',
                                                'published'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'receive'},
                             {'id': 'retract'},
                             {'id': 'verify'},
                             {'id': 'prepublish'},
                             {'id': 'publish'},
                             {'id': 'republish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [{'id': 'copy_to_new',
                                'title': _('Copy to new'),
                                'url': 'workflow_action?action=copy_to_new'}, ],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfileTitle',
                        'getTemplateTitle',
                        'Creator',
                        'Created',
                        'getClientOrderNumber',
                        'getClientReference',
                        'getClientSampleID',
                        'ClientContact',
                        'getSampleTypeTitle',
                        'getSamplePointTitle',
                        'getStorageLocation',
                        'SamplingDeviation',
                        'Priority',
                        'AdHoc',
                        'SamplingDate',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'state_title']},
            ]

    def folderitems(self, full_objects=False):
        workflow = getToolByName(self.context, "portal_workflow")
        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']
            sample = obj.getSample()

            if getSecurityManager().checkPermission(EditResults, obj):
                url = obj.absolute_url() + "/manage_results"
            else:
                url = obj.absolute_url()

            items[x]['Client'] = obj.aq_parent.Title()
            if (hideclientlink is False):
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                    (obj.aq_parent.absolute_url(), obj.aq_parent.Title())
            items[x]['Creator'] = self.user_fullname(obj.Creator())
            items[x]['getRequestID'] = obj.getRequestID()
            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
                 (url, items[x]['getRequestID'])
            items[x]['getSample'] = sample
            items[x]['replace']['getSample'] = \
                "<a href='%s'>%s</a>" % (sample.absolute_url(), sample.Title())

            batch = obj.getBatch()
            if batch:
                items[x]['BatchID'] = batch.getBatchID()
                items[x]['replace']['BatchID'] = "<a href='%s'>%s</a>" % \
                     (batch.absolute_url(), items[x]['BatchID'])
            else:
                items[x]['BatchID'] = ''

            val = obj.Schema().getField('SubGroup').get(obj)
            items[x]['SubGroup'] = val.Title() if val else ''

            samplingdate = obj.getSample().getSamplingDate()
            items[x]['SamplingDate'] = self.ulocalized_time(samplingdate, long_format=1)
            items[x]['getDateReceived'] = self.ulocalized_time(obj.getDateReceived())
            items[x]['getDatePublished'] = self.ulocalized_time(obj.getDatePublished())

            deviation = sample.getSamplingDeviation()
            items[x]['SamplingDeviation'] = deviation and deviation.Title() or ''
            priority = obj.getPriority()
            items[x]['Priority'] = '' # priority.Title()

            items[x]['getStorageLocation'] = sample.getStorageLocation() and sample.getStorageLocation().Title() or ''
            items[x]['AdHoc'] = sample.getAdHoc() and True or ''

            after_icons = ""
            state = workflow.getInfoFor(obj, 'worksheetanalysis_review_state')
            if state == 'assigned':
                after_icons += "<img src='%s/++resource++bika.lims.images/worksheet.png' title='%s'/>" % \
                    (self.portal_url, t(_("All analyses assigned")))
            if workflow.getInfoFor(obj, 'review_state') == 'invalid':
                after_icons += "<img src='%s/++resource++bika.lims.images/delete.png' title='%s'/>" % \
                    (self.portal_url, t(_("Results have been withdrawn")))
            if obj.getLate():
                after_icons += "<img src='%s/++resource++bika.lims.images/late.png' title='%s'>" % \
                    (self.portal_url, t(_("Late Analyses")))
            if samplingdate > DateTime():
                after_icons += "<img src='%s/++resource++bika.lims.images/calendar.png' title='%s'>" % \
                    (self.portal_url, t(_("Future dated sample")))
            if obj.getInvoiceExclude():
                after_icons += "<img src='%s/++resource++bika.lims.images/invoice_exclude.png' title='%s'>" % \
                    (self.portal_url, t(_("Exclude from invoice")))
            if sample.getSampleType().getHazardous():
                after_icons += "<img src='%s/++resource++bika.lims.images/hazardous.png' title='%s'>" % \
                    (self.portal_url, t(_("Hazardous")))
            if after_icons:
                items[x]['after']['getRequestID'] = after_icons

            items[x]['Created'] = self.ulocalized_time(obj.created())

            SamplingWorkflowEnabled =\
                self.context.bika_setup.getSamplingWorkflowEnabled()

            if not samplingdate > DateTime() and SamplingWorkflowEnabled:
                datesampled = self.ulocalized_time(sample.getDateSampled())

                if not datesampled:
                    datesampled = self.ulocalized_time(
                        DateTime(),
                        long_format=1)
                    items[x]['class']['getDateSampled'] = 'provisional'
                sampler = sample.getSampler().strip()
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

            contact = obj.getContact()
            if contact:
                items[x]['ClientContact'] = contact.Title()
                items[x]['replace']['ClientContact'] = "<a href='%s'>%s</a>" % \
                    (contact.absolute_url(), contact.Title())
            else:
                items[x]['ClientContact'] = ""

            # sampling workflow - inline edits for Sampler and Date Sampled
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(SampleSample, obj) \
                and not samplingdate > DateTime():
                items[x]['required'] = ['getSampler', 'getDateSampled']
                items[x]['allow_edit'] = ['getSampler', 'getDateSampled']
                samplers = getUsers(sample, ['Sampler', 'LabManager', 'Manager'])
                username = member.getUserName()
                users = [({'ResultValue': u, 'ResultText': samplers.getValue(u)})
                         for u in samplers]
                items[x]['choices'] = {'getSampler': users}
                Sampler = sampler and sampler or \
                    (username in samplers.keys() and username) or ''
                items[x]['getSampler'] = Sampler

            # These don't exist on ARs
            # XXX This should be a list of preservers...
            items[x]['getPreserver'] = ''
            items[x]['getDatePreserved'] = ''

            # inline edits for Preserver and Date Preserved
            checkPermission = self.context.portal_membership.checkPermission
            if checkPermission(PreserveSample, obj):
                items[x]['required'] = ['getPreserver', 'getDatePreserved']
                items[x]['allow_edit'] = ['getPreserver', 'getDatePreserved']
                preservers = getUsers(obj, ['Preserver', 'LabManager', 'Manager'])
                username = member.getUserName()
                users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
                         for u in preservers]
                items[x]['choices'] = {'getPreserver': users}
                preserver = username in preservers.keys() and username or ''
                items[x]['getPreserver'] = preserver
                items[x]['getDatePreserved'] = self.ulocalized_time(
                    DateTime(),
                    long_format=1)
                items[x]['class']['getPreserver'] = 'provisional'
                items[x]['class']['getDatePreserved'] = 'provisional'

            # Submitting user may not verify results
            if items[x]['review_state'] == 'to_be_verified' and \
               not checkPermission(VerifyOwnResults, obj):
                self_submitted = False
                try:
                    review_history = list(workflow.getInfoFor(obj, 'review_history'))
                    review_history.reverse()
                    for event in review_history:
                        if event.get('action') == 'submit':
                            if event.get('actor') == member.getId():
                                self_submitted = True
                            break
                    if self_submitted:
                        items[x]['after']['state_title'] = \
                             "<img src='++resource++bika.lims.images/submitted-by-current-user.png' title='%s'/>" % \
                             t(_("Cannot verify: Submitted by current user"))
                except Exception:
                    pass

        toggle_cols = self.get_toggle_cols()
        new_states = []
        for i, state in enumerate(self.review_states):
            if state['id'] == self.review_state:
                if 'getSampler' not in toggle_cols \
                   or 'getDateSampled' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('sample')
                    else:
                        state['hide_transitions'] = ['sample', ]
                if 'getPreserver' not in toggle_cols \
                   or 'getDatePreserved' not in toggle_cols:
                    if 'hide_transitions' in state:
                        state['hide_transitions'].append('preserve')
                    else:
                        state['hide_transitions'] = ['preserve', ]
            new_states.append(state)
        self.review_states = new_states

        return items
