# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from zope.interface import implements

from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata

from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IInstrumentLocations
from bika.lims.browser.bika_listing import BikaListingView


class InstrumentLocationsView(BikaListingView):
    """Displays all available instrument locations in a table
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(InstrumentLocationsView, self).__init__(context, request)

        self.contentFilter = {'portal_type': 'InstrumentLocation',
                              'sort_on': 'sortable_title'}

        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=InstrumentLocation',
                                 'icon': '++resource++bika.lims.images/add.png'}}

        self.title = self.context.translate(_("Instrument Locations"))
        self.icon = "++resource++bika.lims.images/instrumenttype_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
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

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for item in items:
            obj = item.get("obj", None)
            if obj is None:
                continue
            item['Description'] = obj.Description()
            item['replace']['Title'] = "<a href='{url}'>{Title}</a>".format(**item)
        return items

schema = ATFolderSchema.copy()


class InstrumentLocations(ATFolder):
    implements(IInstrumentLocations)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(InstrumentLocations, PROJECTNAME)
