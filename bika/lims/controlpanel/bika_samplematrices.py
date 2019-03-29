# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import ISampleMatrices
from bika.lims.permissions import AddSampleMatrix
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements


class SampleMatricesView(BikaListingView):

    def __init__(self, context, request):
        super(SampleMatricesView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'SampleMatrix',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'): {
            'url': 'createObject?type_name=SampleMatrix',
            'permission': AddSampleMatrix,
            'icon': '++resource++bika.lims.images/add.png'
        }}
        self.title = self.context.translate(_("Sample Matrices"))
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/samplematrix_big.png"
        self.description = ""

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Sample Matrix'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [{'id': 'empty'}, ],
             'columns': ['Title', 'Description']},
            {'id': 'active',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Title', 'Description']},
            {'id': 'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Title', 'Description']}
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            items[x]['replace']['Title'] = \
                "<a href='%s'>%s</a>" % (items[x]['url'], items[x]['Title'])

        return items


schema = ATFolderSchema.copy()


class SampleMatrices(ATFolder):
    implements(ISampleMatrices)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(SampleMatrices, PROJECTNAME)
