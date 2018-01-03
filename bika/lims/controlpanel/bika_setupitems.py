# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IAnalysisCategories
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from plone.app.folder.folder import ATFolderSchema, ATFolder
from zope.interface.declarations import implements
from zope.interface import alsoProvides


class BikaSetupItemsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

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
