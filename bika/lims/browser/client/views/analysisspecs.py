# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from bika.lims.utils import isActive
from bika.lims.utils import tmpID
from plone.app.layout.globals.interfaces import IViewView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from zope.interface import implements


class ClientAnalysisSpecsView(BikaListingView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {
            'portal_type': 'AnalysisSpec',
            'sort_on': 'sortable_title',
            'getClientUID': context.UID(),
            'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0
            }
        }
        self.context_actions = {}

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "analysisspecs"

        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisspec_big.png"
        self.title = self.context.translate(_("Analysis Specifications"))

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'title',
                      'replace_url': 'absolute_url'},
            'SampleType': {'title': _('Sample Type'),
                           'index': 'getSampleTypeTitle',
                           'attr': 'getSampleType.Title',
                           'replace_url': 'getSampleType.absolute_url'},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title', 'SampleType']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['title', 'SampleType']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title', 'SampleType']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if isActive(self.context):
            if checkPermission(AddAnalysisSpec, self.context):
                self.context_actions[_('Add')] = \
                    {'url': 'createObject?type_name=AnalysisSpec',
                     'permission': 'Add portal content',
                     'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientAnalysisSpecsView, self).__call__()
