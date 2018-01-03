# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from Products.CMFCore.utils import getToolByName


class ClientSamplePointsView(BikaListingView):
    """This is displayed in the "Sample Points" tab on each client
    """

    def __init__(self, context, request):
        super(ClientSamplePointsView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'SamplePoint',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0},
        }
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "SamplePoints"
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/samplepoint_big.png"
        self.title = self.context.translate(_("Sample Points"))
        self.description = ""

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title',
                      'replace_url': 'absolute_url'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title', 'Description']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['title', 'Description']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title', 'Description']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if checkPermission(AddSamplePoint, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=SamplePoint',
                 'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientSamplePointsView, self).__call__()
