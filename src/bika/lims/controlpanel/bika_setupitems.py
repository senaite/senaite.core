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
             'contentFilter': {'is_active': True},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title', 'Description']},
            {'id': 'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
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
