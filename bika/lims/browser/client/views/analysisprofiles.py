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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import *
from Products.CMFCore.utils import getToolByName


class ClientAnalysisProfilesView(BikaListingView):
    """This is displayed in the Profiles client action,
       in the "Analysis Profiles" tab
    """

    def __init__(self, context, request):
        super(ClientAnalysisProfilesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'AnalysisProfile',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0},
        }

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "analysisprofiles"

        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/analysisprofile_big.png"
        self.title = self.context.translate(_("Analysis Profiles"))
        self.description = ""

        self.columns = {
            'title': {'title': _('Title'),
                      'index': 'sortable_title',
                      'replace_url': 'getURL'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
            'getProfileKey': {'title': _('Profile Key')},

        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title', 'Description', 'getProfileKey']},
            {'id': 'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['title', 'Description', 'getProfileKey']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['title', 'Description', 'getProfileKey']},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        checkPermission = mtool.checkPermission
        if checkPermission(AddAnalysisProfile, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=AnalysisProfile',
                 'permission': 'Add portal content',
                 'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientAnalysisProfilesView, self).__call__()
