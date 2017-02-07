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
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
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

        self.catalog = CATALOG_ANALYSIS_REQUEST_LISTING
        self.contentFilter = {'sort_on': 'Created',
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
                            'attr': 'getRequestID',
                            'replace_url': 'getSampleURL',
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
                        'attr': 'getSampleID',
                        'replace_url': 'getSampleURL',
                        'toggle': True, },
            'BatchID': {'title': _("Batch ID"), 'toggle': True},
            # 'SubGroup': {'title': _('Sub-group')},
            'Client': {'title': _('Client'),
                    'attr': 'getClientTitle',
                    'replace_url': 'getClientURL',
                    'toggle': True},
            'Province': {'title': _('Province'),
                       'toggle': True},
            'District': {'title': _('District'),
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
            # 'AdHoc': {'title': _('Ad-Hoc'),
            #           'toggle': False},
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
            'Printed': {'title': _('Printed'),
                                      'toggle': False},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'sort_on': 'Created',
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
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
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
                               'sort_on': 'Created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'sample'},
                             {'id': 'submit'},
                             {'id': 'cancel'},
                            ],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
            {'id': 'to_be_preserved',
             'title': _('To Be Preserved'),
             'contentFilter': {'review_state': ('to_be_preserved',),
                               'sort_on': 'Created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'preserve'},
                             {'id': 'cancel'},
                             ],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        # 'SubGroup',
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
                        # 'AdHoc',
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
            {'id': 'scheduled_sampling',
             'title': _('Scheduled sampling'),
             'contentFilter': {'review_state': ('scheduled_sampling',),
                               'sort_on': 'Created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'sample'},
                             {'id': 'cancel'},
                             ],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
            {'id': 'sample_due',
             'title': _('Due'),
             'contentFilter': {'review_state': ('to_be_sampled',
                                                'to_be_preserved',
                                                'sample_due'),
                               'sort_on': 'Created',
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
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
                        'getAnalysesNum',
                        'getDateVerified',
                        'state_title']},
           {'id': 'sample_received',
             'title': _('Received'),
             'contentFilter': {'review_state': 'sample_received',
                               'sort_on': 'Created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'prepublish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
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
                               'sort_on': 'Created',
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
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
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
                               'sort_on': 'Created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'publish'},
                             {'id': 'cancel'},
                             ],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
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
                               'sort_on': 'Created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'republish'}],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getAnalysesNum',
                        'getDateVerified',
                        'Printed',
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
                               'sort_on': 'Created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'reinstate'}],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
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
                               'sort_on': 'Created',
                               'sort_order': 'reverse'},
             'transitions': [],
             'custom_actions': [],
             'columns':['getRequestID',
                        'getSample',
                        'BatchID',
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
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
                               'sort_on': 'Created',
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
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
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
                               'sort_on': 'Created',
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
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
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
                               'sort_on': 'Created',
                               'sort_order': 'reverse'},
             'transitions': [],
             'custom_actions': [],
             'columns': ['getRequestID',
                        'getSample',
                        'BatchID',
                        # 'SubGroup',
                        'Client',
                        'Province',
                        'District',
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
                        # 'AdHoc',
                        'getDateSampled',
                        'getSampler',
                        'getDatePreserved',
                        'getPreserver',
                        'getDateReceived',
                        'getDatePublished',
                        'getAnalysesNum',
                        'state_title']},
            ]

    def isItemAllowed(self, obj):
        """
        It checks if the analysis request can be added to the list depending
        on the department filter. It checks the department of each analysis
        service from each analysis belonguing to the given analysis request.
        If department filtering is disabled in bika_setup, will return True.
        @Obj: it is an analysis request object.
        @return: boolean
        """
        if not self.context.bika_setup.getAllowDepartmentFiltering():
            return True
        # Gettin the department from analysis service
        deps = obj.getDepartmentUIDs if hasattr(obj, 'getDepartmentUIDs')\
            else []
        result = True
        if deps:
            # Getting the cookie value
            cookie_dep_uid = self.request.get('filter_by_department_info', '')
            # Comparing departments' UIDs
            deps_uids = set(deps)
            filter_uids = set(cookie_dep_uid.split(','))
            matches = deps_uids & filter_uids
            result = len(matches) > 0
        return result

    def folderitems(self, full_objects=False, classic=True):
        return BikaListingView.folderitems(self, full_objects, classic=False)

    def folderitem(self, obj, item, index):
        # Additional info from AnalysisRequest to be added in the item
        # generated by default by bikalisting.

        # Call the folderitem method from the base class
        item = BikaListingView.folderitem(self, obj, item, index)
        if not item:
            return None
        import pdb; pdb.set_trace()
        # TODO: Deal with this from nrml
        # extract province and district
        item['Province'] = ''  # client.getProvince()
        item['District'] = ''  # client.getDistrict()

        item['Creator'] = self.user_fullname(obj.Creator())
        # If we redirect from the folderitems view we should check if the
        # user has permissions to medify the element or not.
        item['getRequestID'] = obj.getRequestID()
        url = obj.getObjectURL + "?check_edit=1"
        item['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
            (url, item['getRequestID'])
        item['replace']['getProfilesTitle'] = ", ".join(obj.getProfilesTitle())

        analysesnum = obj.getAnalysesNum
        if analysesnum:
            item['getAnalysesNum'] = \
                str(analysesnum[0]) + '/' + str(analysesnum[1])
        else:
            item['getAnalysesNum'] = ''

        item['BatchID'] = batch.getBatchID
        if obj.getBatchID:
            item['replace']['BatchID'] = "<a href='%s'>%s</a>" % \
                (obj.getBatchURL, obj.getBatchID)
        # TODO: SubGroup ???
        # val = obj.Schema().getField('SubGroup').get(obj)
        # item['SubGroup'] = val.Title() if val else ''

        date = obj.getSamplingDate
        item['SamplingDate'] = \
            self.ulocalized_time(date, long_format=1) if date else ''
        date = obj.getDateReceived
        item['getDateReceived'] = \
            self.ulocalized_time(date, long_format=1) if date else ''
        date = obj.getDatePublished
        item['getDatePublished'] = \
            self.ulocalized_time(date, long_format=1) if date else ''
        date = obj.getDateVerified
        item['getDateVerified'] = \
            self.ulocalized_time(date, long_format=1) if date else ''

        if self.printwfenabled:
            item['Printed'] = ''
            printed = obj.getPrinted if hasattr(obj, 'getPrinted') else "0"
            print_icon = ''
            if printed == "0":
                print_icon = "<img src='%s/++resource++bika.lims.images/delete.png' title='%s'>" % \
                    (self.portal_url, t(_("Not printed yet")))
            elif printed == "1":
                print_icon="<img src='%s/++resource++bika.lims.images/ok.png' title='%s'>" % \
                    (self.portal_url, t(_("Printed")))
            elif printed == "2":
                print_icon = "<img src='%s/++resource++bika.lims.images/exclamation.png' title='%s'>" % \
                    (self.portal_url, t(_("Republished after last print")))
            item['after']['Printed'] = print_icon

        item['SamplingDeviation'] = obj.sample.getSamplingDeviationTitle and\
            sample.getSamplingDeviationTitle or ''
        item['Priority'] = obj.getPriority

        item['getStorageLocation'] = obj.getStorageLocationTitle

        after_icons = ""
        states_dict = obj.getObjectWorkflowStates
        if states.get('worksheetanalysis_review_state', '') == 'assigned':
            after_icons += "<img src='%s/++resource++bika.lims.images/worksheet.png' title='%s'/>" % \
                (self.portal_url, t(_("All analyses assigned")))
        if states.get('review_state', '') == 'invalid':
            after_icons += "<img src='%s/++resource++bika.lims.images/delete.png' title='%s'/>" % \
                (self.portal_url, t(_("Results have been withdrawn")))
        if obj.getLate:
            after_icons += "<img src='%s/++resource++bika.lims.images/late.png' title='%s'>" % \
                (self.portal_url, t(_("Late Analyses")))
        if obj.getSamplingDate and obj.getSamplingDate > DateTime():
            after_icons += "<img src='%s/++resource++bika.lims.images/calendar.png' title='%s'>" % \
                (self.portal_url, t(_("Future dated sample")))
        if obj.getInvoiceExclude:
            after_icons += "<img src='%s/++resource++bika.lims.images/invoice_exclude.png' title='%s'>" % \
                (self.portal_url, t(_("Exclude from invoice")))
        if sample.getHazardous:
            after_icons += "<img src='%s/++resource++bika.lims.images/hazardous.png' title='%s'>" % \
                (self.portal_url, t(_("Hazardous")))
        if after_icons:
            item['after']['getRequestID'] = after_icons

        item['Created'] = self.ulocalized_time(obj.created)

        contact = obj.getContact()
        if contact:
            item['ClientContact'] = obj.getContactUsername
            item['replace']['ClientContact'] = "<a href='%s'>%s</a>" % \
                (obj.getContactURL, obj.getContactUsername)
        else:
            item['ClientContact'] = ""

        SamplingWorkflowEnabled = sample.getSamplingWorkflowEnabled
        if SamplingWorkflowEnabled and\
                (not obj.getSamplingDate or not
                    obj.getSamplingDate > DateTime()):
            datesampled = self.ulocalized_time(
                sample.getDateSampled, long_format=True)
            if not datesampled:
                datesampled = self.ulocalized_time(
                    DateTime(), long_format=True)
                item['class']['getDateSampled'] = 'provisional'
            sampler = sample.getSampler
            if sampler:
                item['replace']['getSampler'] = sampler.getSamplerFullName
            if 'Sampler' in self.member.getRoles() and not sampler:
                sampler = self.member.id
                item['class']['getSampler'] = 'provisional'
        else:
            datesampled = ''
            sampler = ''
        item['getDateSampled'] = datesampled
        item['getSampler'] = sampler
        # TODO: Should be allowd people to modify sampler through the list?
        # sampling workflow - inline edits for Sampler and Date Sampled
        # checkPermission = self.context.portal_membership.checkPermission
        # state = self.workflow.getInfoFor(obj, 'review_state')
        # if state == 'to_be_sampled' \
        #         and checkPermission(SampleSample, obj) \
        #         and (not sd or not sd > DateTime()):
        #     item['required'] = ['getSampler', 'getDateSampled']
        #     item['allow_edit'] = ['getSampler', 'getDateSampled']
        #     samplers = getUsers(sample, ['Sampler', 'LabManager', 'Manager'])
        #     username = self.member.getUserName()
        #     users = [({'ResultValue': u, 'ResultText': samplers.getValue(u)})
        #              for u in samplers]
        #     item['choices'] = {'getSampler': users}
        #     Sampler = sampler and sampler or \
        #         (username in samplers.keys() and username) or ''
        #     item['getSampler'] = Sampler

        # These don't exist on ARs
        # XXX This should be a list of preservers...
        item['getPreserver'] = ''
        item['getDatePreserved'] = ''
        # TODO: Should be allowd people to modify sampler through the list?
        # inline edits for Preserver and Date Preserved
        # if checkPermission(PreserveSample, obj):
        #     item['required'] = ['getPreserver', 'getDatePreserved']
        #     item['allow_edit'] = ['getPreserver', 'getDatePreserved']
        #     preservers = getUsers(obj, ['Preserver', 'LabManager', 'Manager'])
        #     username = self.member.getUserName()
        #     users = [({'ResultValue': u, 'ResultText': preservers.getValue(u)})
        #              for u in preservers]
        #     item['choices'] = {'getPreserver': users}
        #     preserver = username in preservers.keys() and username or ''
        #     item['getPreserver'] = preserver
        #     item['getDatePreserved'] = self.ulocalized_time(
        #         DateTime(),
        #         long_format=1)
        #     item['class']['getPreserver'] = 'provisional'
        #     item['class']['getDatePreserved'] = 'provisional'

        # Submitting user may not verify results
        if item['review_state'] == 'to_be_verified':
            allowed = api.user.has_permission(
                VerifyPermission,
                username=self.member.getUserName())
            if allowed and not obj.isUserAllowedToVerify(self.member):
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

        self.member = self.mtool.getAuthenticatedMember()
        roles = self.member.getRoles()
        self.hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        self.editresults = -1
        self.clients = {}

        # Printing workflow enabled?
        # If not, remove the Column
        self.printwfenabled = self.context.bika_setup.getPrintingWorkflowEnabled()
        printed_colname = 'Printed'
        if not self.printwfenabled and printed_colname in self.columns:
            # Remove "Printed" columns
            del self.columns[printed_colname]
            tmprvs = []
            for rs in self.review_states:
                tmprs = rs
                tmprs['columns'] = [c for c in rs.get('columns', []) if
                                    c != printed_colname]
                tmprvs.append(tmprs)
            self.review_states = tmprvs
        elif self.printwfenabled:
            #Print button to choose multiple ARs and print them.
            review_states = []
            for review_state in self.review_states:
                review_state.get('custom_actions', []).extend(
                    [{'id': 'print',
                      'title': _('Print'),
                      'url': 'workflow_action?action=print'}, ])
                review_states.append(review_state)
            self.review_states = review_states

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
