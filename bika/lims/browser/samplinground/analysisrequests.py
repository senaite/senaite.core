# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analysisrequest import AnalysisRequestAddView as _ARAV
from bika.lims.browser.analysisrequest import AnalysisRequestsView as _ARV
from bika.lims.permissions import *
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from bika.lims.utils import t
from copy import copy


class AnalysisRequestsView(_ARV, _ARAV):
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        SamplingWorkflowEnabled = self.context.bika_setup.getSamplingWorkflowEnabled()
        self.columns = {
            'securitySealIntact': {'title': _('Security Seal Intact'),
                                  'toggle': True},
            'samplingRoundTemplate': {'title': _('Sampling Round Template'),
                                      'toggle': True},
            'getId': {'title': _('Request ID'),
                             'index': 'getId'},
            'getDateSampled': {'title': _('Date Sampled'),
                               'index': 'getDateSampled',
                               'toggle': True,
                               'input_class': 'datetimepicker',
                               'input_width': '10'},
            'state_title': {'title': _('State'),
                            'index': 'review_state'},
            'getProfilesTitle': {'title': _('Profile'),
                                'toggle': False},
            'getTemplateTitle': {'title': _('Template'),
                                 'toggle': False},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True,
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
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
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
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
                         'state_title']},
           {'id': 'sample_received',
             'title': _('Received'),
             'contentFilter': {'review_state': 'sample_received',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'prepublish'},
                             {'id': 'cancel'},
                             {'id': 'reinstate'}],
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
                         'state_title']},
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
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
                         'state_title']},
            {'id': 'verified',
             'title': _('Verified'),
             'contentFilter': {'review_state': 'verified',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'publish'}],
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
                         'state_title']},
            {'id': 'published',
             'title': _('Published'),
             'contentFilter': {'review_state': ('published', 'invalid'),
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'republish'}],
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
                         'state_title']},
            {'id': 'cancelled',
             'title': _('Cancelled'),
             'contentFilter': {'is_active': False,
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [{'id': 'reinstate'}],
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
                         'state_title']},
            {'id': 'invalid',
             'title': _('Invalid'),
             'contentFilter': {'review_state': 'invalid',
                               'sort_on': 'created',
                               'sort_order': 'reverse'},
             'transitions': [],
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
                         'state_title']},
            {'id': 'assigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/assigned.png'/>" % (
                       t(_("Assigned")), self.portal_url),
             'contentFilter': {'assigned_state': 'assigned',
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
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
                         'state_title']},
            {'id': 'unassigned',
             'title': "<img title='%s'\
                       src='%s/++resource++bika.lims.images/unassigned.png'/>" % (
                       t(_("Unassigned")), self.portal_url),
             'contentFilter': {'assigned_state': 'unassigned',
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
             'custom_transitions': [],
             'columns': ['securitySealIntact',
                         'getId',
                         'samplingRoundTemplate',
                         'getDateSampled',
                         'state_title']},
            ]

    def contentsMethod(self, contentFilter):
        pc = getToolByName(self.context, 'portal_catalog')
        if 'SamplingRoundUID' not in contentFilter.keys():
            contentFilter['SamplingRoundUID'] = self.context.UID()
        return pc(contentFilter)

    def __call__(self):
        self.context_actions = {}
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(AddAnalysisRequest, self.portal):
            # We give the number of analysis request templates in order to fill out the analysis request form
            # automatically :)
            num_art = len(self.context.ar_templates)
            self.context_actions[self.context.translate(_('Add new'))] = {
                'url': self.context.aq_parent.absolute_url() + \
                    "/portal_factory/"
                    "AnalysisRequest/Request new analyses/ar_add?samplinground="
                    + self.context.UID() + "&ar_count=" + str(num_art),
                'icon': '++resource++bika.lims.images/add.png'}
        return super(AnalysisRequestsView, self).__call__()

    def folderitem(self, obj, item, index):
        # Call the folderitem method from the base class
        item = _ARV.folderitem(self, obj, item, index)
        # In sampling rounds, analysis request list will be listed per Sample
        # Partition/Container Obtaining analysis requests
        # TODO-performance: don't get the full object
        obj = obj.getObject()
        # Getting the sampling round template uid
        srTemplateUID = obj.getSamplingRound().sr_template if obj.getSamplingRound().sr_template else ''
        # Getting the sampling round object
        catalog = getToolByName(self.context, 'uid_catalog')
        srTemplateObj = catalog(UID=srTemplateUID)[0].getObject() if catalog(UID=srTemplateUID) else None
        item['samplingRoundTemplate'] = ''
        if srTemplateObj:
            item['samplingRoundTemplate'] = srTemplateObj.title
            item['replace']['samplingRoundTemplate'] = \
                "<a href='%s'>%s</a>" % (
                srTemplateObj.absolute_url, item['samplingRoundTemplate'])
        item['securitySealIntact'] = ''
        return item
