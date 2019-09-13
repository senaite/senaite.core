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

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from senaite.core import bikaMessageFactory as _
from senaite.core.browser.bika_listing import BikaListingView
from senaite.core.config import PROJECTNAME
from senaite.core.interfaces import ISubGroups
from senaite.core.permissions import AddSubGroup
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from zope.interface.declarations import implements


class SubGroupsView(BikaListingView):

    def __init__(self, context, request):
        super(SubGroupsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'SubGroup',
                              'sort_on': 'sortable_title'}
        self.context_actions = {
            _('Add'): {
                'url': 'createObject?type_name=SubGroup',
                'permission': AddSubGroup,
                'icon': '++resource++senaite.core.images/add.png'
            }
        }
        self.icon = self.portal_url + \
            "/++resource++senaite.core.images/batch_big.png"
        self.title = self.context.translate(_("Sub-groups"))
        self.description = ""

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Sub-group'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'SortKey': {'title': _('Sort Key')},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title', 'Description', 'SortKey']},
            {'id': 'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title', 'Description', 'SortKey']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title', 'Description', 'SortKey']},
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                (items[x]['url'], items[x]['Title'])

        return items


schema = ATFolderSchema.copy()


class SubGroups(ATFolder):
    implements(ISubGroups)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(SubGroups, PROJECTNAME)
