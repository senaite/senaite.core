# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from plone import api
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import getUsers
from bika.lims.workflow import getTransitionDate
from bika.lims.permissions import *
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.utils import to_utf8, getUsers
from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


class AnalysisRequestsView(BikaListingView):
    """Base for all lists of ARs
    """
    template = ViewPageTemplateFile("templates/analysisrequests.pt")
    ar_add = ViewPageTemplateFile("templates/ar_add.pt")
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)

        request.set('disable_plone.rightcolumn', 1)

        self.catalog = "bika_catalog"
        self.contentFilter = {'portal_type': 'AnalysisRequest',
                              'sort_on': 'created',
                              'sort_order': 'reverse',
                              'path': {"query": "/", "level": 0},
                              'cancellation_state': 'active',
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
        self.title = self.context.translate(_("Analysis Requests"))
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
                               'toggle': SamplingWorkflowEnabled,
                               'input_class': 'datetimepicker_nofuture',
                               'input_width': '10'},
            'getDateVerified': {'title': _('Date Verified'),
                                'input_width': '10'},
            'getSampler': {'title': _('Sampler'),
                           'toggle': SamplingWorkflowEnabled},
            'getDatePreserved': {'title': _('Date Preserved'),
                                 'toggle': user_is_preserver,
                                 'input_class': 'datetimepicker_nofuture',
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
            'getProfilesTitle': {'title': _('Profile'),
                                'index': 'getProfilesTitle',
                                'toggle': False},
            'getAnalysesNum': {'title': _('Number of Analyses'),
                               'index': 'getAnalysesNum',
                               'sortable': True,
                               'toggle': False},
            'getTemplateTitle': {'title': _('Template'),
                                 'index': 'getTemplateTitle',
                                 'toggle': False},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'sort_on': 'created',
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
             'custom_actions': [],
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
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
            {'id': 'to_be_sampled',
             'title': _('To Be Sampled'),
             'contentFilter': {'review_state': ('to_be_sampled',),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'sample'},
                             {'id': 'submit'},
                             {'id': 'cancel'},
                            ],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
            {'id': 'to_be_preserved',
             'title': _('To Be Preserved'),
             'contentFilter': {'review_state': ('to_be_preserved',),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'preserve'},
                             {'id': 'cancel'},
                             ],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
            {'id': 'scheduled_sampling',
             'title': _('Scheduled sampling'),
             'contentFilter': {'review_state': ('scheduled_sampling',),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'sample'},
                             {'id': 'cancel'},
                             ],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
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
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
           {'id': 'sample_received',
             'title': _('Received'),
             'contentFilter': {'review_state': 'sample_received',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'prepublish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
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
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
                        'getDateReceived']},
            {'id': 'verified',
             'title': _('Verified'),
             'contentFilter': {'review_state': 'verified',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'publish'},
                             {'id': 'cancel'},
                             ],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
                        'getDateReceived']},
            {'id': 'published',
             'title': _('Published'),
             'contentFilter': {'review_state': ('published', 'invalid'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'republish'}],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
                        'getDatePublished']},
            {'id': 'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'cancellation_state': 'cancelled',
                               'review_state': (
                                   'sample_registered',
                                   'to_be_sampled',
                                   'to_be_preserved',
                                   'sample_due',
                                   'sample_received',
                                   'to_be_verified',
                                   'attachment_due',
                                   'verified',
                                   'published'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
            {'id': 'invalid',
             'title': _('Invalid'),
             'contentFilter': {'review_state': 'invalid',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [],
             'custom_actions': [],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
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
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
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
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
            {'id': 'rejected',
             'title': _('Rejected'),
             'contentFilter': {'review_state': 'rejected',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        'SubGroup',
                        'Client',
                        'getProfilesTitle',
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
                        'getAnalysesNum',
                        'state_title']},
            ]

    def folderitem(self, obj, item, index):
        # Additional info from AnalysisRequest to be added in the item generated
        # by default by bikalisting.

        # Call the folderitem method from the base class
        item = BikaListingView.folderitem(self, obj, item, index)
        if not item:
            return None

        member = self.mtool.getAuthenticatedMember()
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        sample = obj.getSample()
        url = obj.absolute_url()
        if getSecurityManager().checkPermission(EditResults, obj):
            url += "/manage_results"

        item['Client'] = obj.aq_parent.Title()
        if (hideclientlink == False):
            item['replace']['Client'] = "<a href='%s'>%s</a>" % \
                (obj.aq_parent.absolute_url(), obj.aq_parent.Title())
        item['Creator'] = self.user_fullname(obj.Creator())
        item['getRequestID'] = obj.getRequestID()
        item['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
             (url, item['getRequestID'])
        item['getSample'] = sample
        item['replace']['getSample'] = \
            "<a href='%s'>%s</a>" % (sample.absolute_url(), sample.Title())

        item['replace']['getProfilesTitle'] = ", ".join(
            [p.Title() for p in obj.getProfiles()])

        analysesnum = obj.getAnalysesNum()
        if analysesnum:
            item['getAnalysesNum'] = str(analysesnum[0]) + '/' + str(analysesnum[1])
        else:
            item['getAnalysesNum'] = ''

        batch = obj.getBatch()
        if batch:
            item['BatchID'] = batch.getBatchID()
            item['replace']['BatchID'] = "<a href='%s'>%s</a>" % \
                 (batch.absolute_url(), item['BatchID'])
        else:
            item['BatchID'] = ''

        val = obj.Schema().getField('SubGroup').get(obj)
        item['SubGroup'] = val.Title() if val else ''

        sd = obj.getSample().getSamplingDate()
        item['SamplingDate'] = \
            self.ulocalized_time(sd, long_format=1) if sd else ''
        item['getDateReceived'] = \
            self.ulocalized_time(obj.getDateReceived())
        item['getDatePublished'] = \
            self.ulocalized_time(getTransitionDate(obj, 'publish'))
        item['getDateVerified'] = \
            self.ulocalized_time(getTransitionDate(obj, 'verify'))

        deviation = sample.getSamplingDeviation()
        item['SamplingDeviation'] = deviation and deviation.Title() or ''
        priority = obj.getPriority()
        item['Priority'] = '' # priority.Title()

        item['getStorageLocation'] = sample.getStorageLocation() and sample.getStorageLocation().Title() or ''
        item['AdHoc'] = sample.getAdHoc() and True or ''

        after_icons = ""
        state = self.workflow.getInfoFor(obj, 'worksheetanalysis_review_state')
        if state == 'assigned':
            after_icons += "<img src='%s/++resource++bika.lims.images/worksheet.png' title='%s'/>" % \
                (self.portal_url, t(_("All analyses assigned")))
        if self.workflow.getInfoFor(obj, 'review_state') == 'invalid':
            after_icons += "<img src='%s/++resource++bika.lims.images/delete.png' title='%s'/>" % \
                (self.portal_url, t(_("Results have been withdrawn")))
        if obj.getLate():
            after_icons += "<img src='%s/++resource++bika.lims.images/late.png' title='%s'>" % \
                (self.portal_url, t(_("Late Analyses")))
        if sd and sd > DateTime():
            after_icons += "<img src='%s/++resource++bika.lims.images/calendar.png' title='%s'>" % \
                (self.portal_url, t(_("Future dated sample")))
        if obj.getInvoiceExclude():
            after_icons += "<img src='%s/++resource++bika.lims.images/invoice_exclude.png' title='%s'>" % \
                (self.portal_url, t(_("Exclude from invoice")))
        if sample.getSampleType().getHazardous():
            after_icons += "<img src='%s/++resource++bika.lims.images/hazardous.png' title='%s'>" % \
                (self.portal_url, t(_("Hazardous")))
        if after_icons:
            item['after']['getRequestID'] = after_icons

        item['Created'] = self.ulocalized_time(obj.created())

        contact = obj.getContact()
        if contact:
            item['ClientContact'] = contact.Title()
            item['replace']['ClientContact'] = "<a href='%s'>%s</a>" % \
                (contact.absolute_url(), contact.Title())
        else:
            item['ClientContact'] = ""

        SamplingWorkflowEnabled = sample.getSamplingWorkflowEnabled()
        if SamplingWorkflowEnabled and (not sd or not sd > DateTime()):
            datesampled = self.ulocalized_time(
                sample.getDateSampled(), long_format=True)
            if not datesampled:
                datesampled = self.ulocalized_time(
                    DateTime(), long_format=True)
                item['class']['getDateSampled'] = 'provisional'
            sampler = sample.getSampler().strip()
            if sampler:
                item['replace']['getSampler'] = self.user_fullname(sampler)
            if 'Sampler' in member.getRoles() and not sampler:
                sampler = member.id
                item['class']['getSampler'] = 'provisional'
        else:
            datesampled = ''
            sampler = ''
        item['getDateSampled'] = datesampled
        item['getSampler'] = sampler

        # sampling workflow - inline edits for Sampler and Date Sampled
        checkPermission = self.context.portal_membership.checkPermission
        state = self.workflow.getInfoFor(obj, 'review_state')
        if state == 'to_be_sampled' \
                and checkPermission(SampleSample, obj) \
                and (not sd or not sd > DateTime()):
            item['required'] = ['getSampler', 'getDateSampled']
            item['allow_edit'] = ['getSampler', 'getDateSampled']
            samplers = getUsers(sample, ['Sampler', 'LabManager', 'Manager'])
            username = member.getUserName()
            users = [({'ResultValue': u, 'ResultText': samplers.getValue(u)})
                     for u in samplers]
            item['choices'] = {'getSampler': users}
            Sampler = sampler and sampler or \
                (username in samplers.keys() and username) or ''
            item['getSampler'] = Sampler

        # These don't exist on ARs
        # XXX This should be a list of preservers...
        item['getPreserver'] = ''
        item['getDatePreserved'] = ''

        # inline edits for Preserver and Date Preserved
        checkPermission = self.context.portal_membership.checkPermission
        if checkPermission(PreserveSample, obj):
            item['required'] = ['getPreserver', 'getDatePreserved']
            item['allow_edit'] = ['getPreserver', 'getDatePreserved']
            preservers = getUsers(obj, ['Preserver', 'LabManager', 'Manager'])
            username = member.getUserName()
            users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
                     for u in preservers]
            item['choices'] = {'getPreserver': users}
            preserver = username in preservers.keys() and username or ''
            item['getPreserver'] = preserver
            item['getDatePreserved'] = self.ulocalized_time(
                DateTime(),
                long_format=1)
            item['class']['getPreserver'] = 'provisional'
            item['class']['getDatePreserved'] = 'provisional'

        # Submitting user may not verify results
        if item['review_state'] == 'to_be_verified':
            username = member.getUserName()
            allowed = api.user.has_permission(VerifyPermission,
                                              username=username)
            if allowed and not obj.isUserAllowedToVerify(member):
                item['after']['state_title'] = \
                     "<img src='++resource++bika.lims.images/submitted-by-current-user.png' title='%s'/>" % \
                     t(_("Cannot verify: Submitted by current user"))

        return item

    @property
    def copy_to_new_allowed(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(ManageAnalysisRequests, self.context) \
            or mtool.checkPermission(ModifyPortalContent, self.context):
            return True
        return False

    def __call__(self):
        self.workflow = getToolByName(self.context, "portal_workflow")
        self.mtool = getToolByName(self.context, 'portal_membership')

        # Only "BIKA: ManageAnalysisRequests" may see the copy to new button.
        # elsewhere it is hacked in where required.
        if self.copy_to_new_allowed:
            review_states = []
            for review_state in self.review_states:
                review_state.get('custom_actions', []).extend(
                    [{'id': 'copy_to_new',
                      'title': _('Copy to new'),
                      'url': 'workflow_action?action=copy_to_new'}, ])
                review_states.append(review_state)
            self.review_states = review_states

        # Hide Preservation/Sampling workflow actions if the edit columns
        # are not displayed.
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

        return super(AnalysisRequestsView, self).__call__()
