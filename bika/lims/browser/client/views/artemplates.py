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


class ClientARTemplatesView(BikaListingView):
    """This is displayed in the Templates client action,
       in the "AR Templates" tab
    """

    def __init__(self, context, request):
        super(ClientARTemplatesView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'ARTemplate',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0},
        }

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "artemplates"
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/artemplate_big.png"
        self.title = self.context.translate(_("Sample Templates"))
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
             'contentFilter': {'is_active': True},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title', 'Description']},
            {'id': 'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
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
        if checkPermission(AddARTemplate, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=ARTemplate',
                 'permission': 'Add portal content',
                 'icon': '++resource++bika.lims.images/add.png'}
        return super(ClientARTemplatesView, self).__call__()
