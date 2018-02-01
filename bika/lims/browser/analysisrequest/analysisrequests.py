# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
import traceback
from plone.api import user

from DateTime import DateTime
from Products.Archetypes import PloneMessageFactory as PMF
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser.analysisrequest.analysisrequests_filter_bar \
    import AnalysisRequestsBikaListingFilterBar
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import PRIORITIES
from bika.lims.permissions import *
from bika.lims.permissions import Verify as VerifyPermission
from bika.lims.utils import getUsers
from bika.lims.utils import t
from collective.taskqueue.interfaces import ITaskQueue
from plone.app.layout.globals.interfaces import IViewView
from plone.protect import CheckAuthenticator
from plone.protect import PostOnly
from zope.component import queryUtility
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
        # Setting up the catalog and query dictionary
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

        # Check if the filter bar functionality is activated or not
        self.filter_bar_enabled =\
            self.context.bika_setup.\
            getDisplayAdvancedFilterBarForAnalysisRequests()

        self.columns = {
            'Priority': {
                'title': '',
                'index': 'getPrioritySortkey',
                'sortable': True,},
            'Progress': {
                'title': 'Progress',
                'sortable': False,
                'toggle': True},
            'getId': {
                'title': _('Request ID'),
                'attr': 'getId',
                'replace_url': 'getURL',
                'index': 'getId'},
            'getClientOrderNumber': {
                'title': _('Client Order'),
                'sortable': False,
                'toggle': True},
            'Creator': {
                'title': PMF('Creator'),
                'sortable': False,
                'toggle': True},
            'Created': {
                'title': PMF('Date Created'),
                'index': 'created',
                'toggle': False},
            'getSample': {
                'title': _("Sample"),
                'attr': 'getSampleID',
                'index': 'getSampleID',
                'replace_url': 'getSampleURL',
                'toggle': True, },
            'BatchID': {
                'title': _("Batch ID"),
                'sortable': False,
                'toggle': True},
            'Client': {
                'title': _('Client'),
                'index': 'getClientTitle',
                'attr': 'getClientTitle',
                'replace_url': 'getClientURL',
                'toggle': True},
            'Province': {
                'title': _('Province'),
                'sortable': True,
                'index': 'getProvince',
                'attr': 'getProvince',
                'toggle': True},
            'District': {
                'title': _('District'),
                'sortable': True,
                'index': 'getDistrict',
                'attr': 'getDistrict',
                'toggle': True},
            'getClientReference': {
                'title': _('Client Ref'),
                'sortable': False,
                'toggle': True},
            'getClientSampleID': {
                'title': _('Client SID'),
                'toggle': True},
            'ClientContact': {
                'title': _('Contact'),
                'sortable': False,
                'toggle': False},
            'getSampleTypeTitle': {
                'title': _('Sample Type'),
                'sortable': False,
                'toggle': True},
            'getSamplePointTitle': {
                'title': _('Sample Point'),
                'sortable': False,
                'toggle': False},
            'getStorageLocation': {
                'title': _('Storage Location'),
                'sortable': False,
                'toggle': False},
            'SamplingDeviation': {
                'title': _('Sampling Deviation'),
                'sortable': False,
                'toggle': False},
            # 'AdHoc': {'title': _('Ad-Hoc'),
            #           'toggle': False},
            'SamplingDate': {
                'title': _('Expected Sampling Date'),
                'index': 'getSamplingDate',
                'toggle': SamplingWorkflowEnabled},
            'getDateSampled': {
                'title': _('Date Sampled'),
                'toggle': True,
                'input_class': 'datetimepicker_nofuture',
                'input_width': '10'},
            'getDateVerified': {
                'title': _('Date Verified'),
                'input_width': '10'},
            'getSampler': {
                'title': _('Sampler'),
                'toggle': SamplingWorkflowEnabled},
            'getDatePreserved': {
                'title': _('Date Preserved'),
                'toggle': False,
                'input_class': 'datetimepicker_nofuture',
                'input_width': '10',
                'sortable': False},  # no datesort without index
            'getPreserver': {
                'title': _('Preserver'),
                'sortable': False,
                'toggle': False},
            'getDateReceived': {
                'title': _('Date Received'),
                'toggle': False},
            'getDatePublished': {
                'title': _('Date Published'),
                'toggle': False},
            'state_title': {
                'title': _('State'),
                'sortable': False,
                'index': 'review_state'},
            'getProfilesTitle': {
                'title': _('Profile'),
                'sortable': False,
                'toggle': False},
            'getAnalysesNum': {
                'title': _('Number of Analyses'),
                'sortable': False,
                'toggle': False},
            'getTemplateTitle': {
                'title': _('Template'),
                'sortable': False,
                'toggle': False},
            'Printed': {
                'title': _('Printed'),
                'sortable': False,
                'index': 'getPrinted',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                         'Progress',
                        'getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [],
             'columns': ['getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns':['getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['Priority',
                        'getId',
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
             'custom_transitions': [{
                 'id': 'print_stickers',
                 'title': _('Print stickers'),
                 'url': 'workflow_action?action=print_stickers'}],
             'columns': ['getId',
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
        @Obj: it is an analysis request brain.
        @return: boolean
        """
        if self.filter_bar_enabled and not self.filter_bar_check_item(obj):
            return False
        if not self.context.bika_setup.getAllowDepartmentFiltering():
            return True
        # Getting the department from analysis service
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

    def folderitems(self, full_objects=False, classic=False):
        # We need to get the portal catalog here in roder to save process
        # while iterating over folderitems
        self.portal_catalog = getToolByName(self.context, 'portal_catalog')
        return BikaListingView.folderitems(self, full_objects, classic)

    def folderitem(self, obj, item, index):
        # Additional info from AnalysisRequest to be added in the item
        # generated by default by bikalisting.
        # Call the folderitem method from the base class
        item = BikaListingView.folderitem(self, obj, item, index)
        if not item:
            return None
        # This variable will contain the full analysis request if there is
        # need to work with the full object instead of the brain
        full_object = None
        item['Creator'] = self.user_fullname(obj.Creator)
        # If we redirect from the folderitems view we should check if the
        # user has permissions to medify the element or not.
        priority_sort_key = obj.getPrioritySortkey
        if not priority_sort_key:
            # Default priority is Medium = 3.
            # The format of PrioritySortKey is <priority>.<created>
            priority_sort_key = '3.%s' % obj.created.ISO8601()
        priority = priority_sort_key.split('.')[0]
        priority_text = PRIORITIES.getValue(priority)
        priority_div = '<div class="priority-ico priority-%s"><span class="notext">%s</span><div>'
        item['replace']['Priority'] = priority_div % (priority, priority_text)
        item['replace']['getProfilesTitle'] = obj.getProfilesTitleStr

        analysesnum = obj.getAnalysesNum
        if analysesnum:
            num_verified = str(analysesnum[0])
            num_total = str(analysesnum[1])
            item['getAnalysesNum'] = '{0}/{1}'.format(num_verified, num_total)
        else:
            item['getAnalysesNum'] = ''

        # Progress
        num_verified = 0
        num_submitted = 0
        num_total = 0
        if analysesnum and len(analysesnum) > 1:
            num_verified = analysesnum[0]
            num_total = analysesnum[1]
            num_submitted = num_total - num_verified
            if len(analysesnum) > 2:
                num_wo_results = analysesnum[2]
                num_submitted = num_total - num_verified - num_wo_results
        num_steps_total = num_total * 2
        num_steps = (num_verified * 2) + (num_submitted)
        progress_perc = 0
        if num_steps > 0 and num_steps_total > 0:
            progress_perc = (num_steps * 100) / num_steps_total
        progress = '<div class="progress-bar-container">' + \
                   '<div class="progress-bar" style="width:{0}%"></div>' + \
                   '<div class="progress-perc">{0}%</div></div>'
        item['replace']['Progress'] = progress.format(progress_perc)

        item['BatchID'] = obj.getBatchID
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
        item['SamplingDeviation'] = obj.getSamplingDeviationTitle

        item['getStorageLocation'] = obj.getStorageLocationTitle

        after_icons = ""
        # Getting a dictionary with each workflow id and current state in it
        states_dict = obj.getObjectWorkflowStates
        if states_dict.get('worksheetanalysis_review_state', '') == 'assigned':
            after_icons += "<img src='%s/++resource++bika.lims.images/worksheet.png' title='%s'/>" % \
                (self.portal_url, t(_("All analyses assigned")))
        if states_dict.get('review_state', '') == 'invalid':
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
        if obj.getHazardous:
            after_icons += "<img src='%s/++resource++bika.lims.images/hazardous.png' title='%s'>" % \
                (self.portal_url, t(_("Hazardous")))
        if after_icons:
            item['after']['getId'] = after_icons

        item['Created'] = self.ulocalized_time(obj.created)
        if obj.getContactUID:
            item['ClientContact'] = obj.getContactFullName
            item['replace']['ClientContact'] = "<a href='%s'>%s</a>" % \
                (obj.getContactURL, obj.getContactFullName)
        else:
            item['ClientContact'] = ""
        # TODO-performance: If SamplingWorkflowEnabled, we have to get the
        # full object to check the user permissions, so far this is
        # a performance hit.
        if obj.getSamplingWorkflowEnabled:
            # We don't do anything with Sampling Date. User can modify Sampling date
            # inside AR view. In this listing view, we only let the user to edit Date Sampled
            # and Sampler if he wants to make 'sample' transaction.
            if not obj.getDateSampled:
                datesampled = self.ulocalized_time(
                    DateTime(), long_format=True)
                item['class']['getDateSampled'] = 'provisional'
            else:
                datesampled = self.ulocalized_time(obj.getDateSampled, long_format=True)

            sampler = obj.getSampler
            if sampler:
                item['replace']['getSampler'] = obj.getSamplerFullName
            if 'Sampler' in self.roles and not sampler:
                sampler = self.member.id
                item['class']['getSampler'] = 'provisional'
            # sampling workflow - inline edits for Sampler and Date Sampled
            if states_dict.get('review_state', '') == 'to_be_sampled':
                # We need to get the full object in order to check
                # the permissions
                full_object = obj.getObject()
                checkPermission =\
                    self.context.portal_membership.checkPermission
                if checkPermission(SampleSample, full_object):
                    item['required'] = ['getSampler', 'getDateSampled']
                    item['allow_edit'] = ['getSampler', 'getDateSampled']
                    # TODO-performance: hit performance while getting the
                    # sample object...
                    # TODO Can LabManagers be a Sampler?!
                    samplers = getUsers(
                        full_object.getSample(),
                        ['Sampler', ])
                    username = self.member.getUserName()
                    users = [({
                        'ResultValue': u,
                        'ResultText': samplers.getValue(u)})
                            for u in samplers]
                    item['choices'] = {'getSampler': users}
                    Sampler = sampler and sampler or \
                        (username in samplers.keys() and username) or ''
                    sampler = Sampler
                else:
                    datesampled = self.ulocalized_time(obj.getDateSampled, long_format=True)
                    sampler = obj.getSamplerFullName if obj.getSampler else ''
        else:
            datesampled = self.ulocalized_time(obj.getDateSampled, long_format=True)
            sampler = ''
        item['getDateSampled'] = datesampled
        item['getSampler'] = sampler

        # These don't exist on ARs
        # XXX This should be a list of preservers...
        item['getPreserver'] = ''
        item['getDatePreserved'] = ''
        # TODO-performance: If inline preservation wants to be used, we
        # have to get the full object to check the user permissions, so
        # far this is a performance hit.
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
        # Thee conditions to improve performance, some functions to check
        # the condition need to get the full analysis request.
        if states_dict.get('review_state', '') == 'to_be_verified':
            allowed = user.has_permission(
                VerifyPermission,
                username=self.member.getUserName())
            # TODO-performance: isUserAllowedToVerify getts all analysis
            # objects inside the analysis request.
            if allowed:
                # Gettin the full object if not get before
                full_object = full_object if full_object else obj.getObject()
                if not full_object.isUserAllowedToVerify(self.member):
                    item['after']['state_title'] = \
                         "<img src='++resource++bika.lims.images/submitted-by-current-user.png' title='%s'/>" % \
                         t(_("Cannot verify: Submitted by current user"))
        return item

    def pending_tasks(self):
        task_queue = queryUtility(ITaskQueue, name='ar-create')
        if task_queue is None:
            return 0
        return len(task_queue)

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
        self.roles = self.member.getRoles()
        self.hideclientlink = 'RegulatoryInspector' in self.roles \
            and 'Manager' not in self.roles \
            and 'LabManager' not in self.roles \
            and 'LabClerk' not in self.roles

        if self.context.portal_type == "AnalysisRequestsFolder" and \
                (self.mtool.checkPermission(AddAnalysisRequest, self.context)):
            self.context_actions[_('Add')] = \
                {'url': "ar_add?ar_count=1",
                 'icon': '++resource++bika.lims.images/add.png'}

        self.editresults = -1
        self.clients = {}
        # self.user_is_preserver = 'Preserver' in self.roles
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
                review_state.get('custom_transitions', []).extend(
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
                review_state.get('custom_transitions', []).extend(
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

    def getFilterBar(self):
        """
        This function creates an instance of BikaListingFilterBar if the
        class has not created one yet.
        :returns: a BikaListingFilterBar instance
        """
        self._advfilterbar = self._advfilterbar if self._advfilterbar else \
            AnalysisRequestsBikaListingFilterBar(
                context=self.context, request=self.request)
        return self._advfilterbar

    def getDefaultAddCount(self):
        return self.context.bika_setup.getDefaultNumberOfARsToAdd()


class QueuedAnalysisRequestsCount():

    def __call__(self):
        """Returns the number of tasks in the queue ar-create, responsible of
        creating Analysis Requests asynchronously"""
        try:
            PostOnly(self.context.REQUEST)
        except:
            logger.error(traceback.format_exc())
            return json.dumps({'count': 0})
        try:
            CheckAuthenticator(self.request.form)
        except:
            logger.error(traceback.format_exc())
            return json.dumps({'count': 0})
        task_queue = queryUtility(ITaskQueue, name='ar-create')
        count = len(task_queue) if task_queue is not None else 0
        return json.dumps({'count': count})
