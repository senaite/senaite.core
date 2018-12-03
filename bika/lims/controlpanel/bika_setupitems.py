# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView


class BikaSetupItemsView(BikaListingView):

    def __init__(self, context, request, typename, iconfilename):
        super(BikaSetupItemsView, self).__init__(context, request)
        self.show_select_column = True
        self.icon = self.portal_url + "/++resource++bika.lims.images/" + iconfilename
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {
            'portal_type': typename,
            'sort_on': 'sortable_title'
        }
        self.context_actions = {
            _('Add'): {
                'url': 'createObject?type_name='+typename,
                'icon': '++resource++bika.lims.images/add.png'
            }
        }
        self.columns = {
            'Title': {
                'title': _('Title'),
                'index': 'sortable_title',
                'replace_url': 'absolute_url'
            },
            'Description': {
                'title': _('Description'),
                'index': 'description',
                'attr': 'Description'
            },
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title', 'Description']},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title', 'Description']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title', 'Description']},
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)
