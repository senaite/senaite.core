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

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IContainers
from bika.lims.permissions import AddContainer
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements


class ContainersView(BikaListingView):

    def __init__(self, context, request):
        super(ContainersView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'Container',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=Container',
                                 'permission': AddContainer,
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Containers"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/container_big.png"
        self.description = ""

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Container'),
                      'index':'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'ContainerType': {'title': _('Container Type'),
                              'toggle': True},
            'Capacity': {'title': _('Capacity'),
                         'toggle': True},
            'Pre-preserved': {'title': _('Pre-preserved'),
                             'toggle': True},
        }

        self.review_states = [ # leave these titles and ids alone
            {'id':'default',
             'contentFilter': {'is_active': True},
             'title': _('Active'),
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'ContainerType',
                         'Capacity',
                         'Pre-preserved']},
            {'id':'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'ContainerType',
                         'Capacity',
                         'Pre-preserved']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns': ['Title',
                         'Description',
                         'ContainerType',
                         'Capacity',
                         'Pre-preserved']},
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['ContainerType'] = obj.getContainerType() and obj.getContainerType().Title() or ''
            items[x]['Capacity'] = obj.getCapacity() and "%s" % \
                (obj.getCapacity()) or ''
            pre = obj.getPrePreserved()
            pres = obj.getPreservation()
            items[x]['Pre-preserved'] = ''
            items[x]['after']['Pre-preserved'] = pre \
                and "<a href='%s'>%s</a>" % (pres.absolute_url(), pres.Title()) \
                or ''

            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items


schema = ATFolderSchema.copy()

class Containers(ATFolder):
    implements(IContainers)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Containers, PROJECTNAME)
