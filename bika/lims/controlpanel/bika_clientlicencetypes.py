# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from plone.supermodel import model
from plone.dexterity.content import Container
from zope.interface import implements
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.controlpanel.bika_setupitems import BikaSetupItemsView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.interfaces import IClientLicenceTypes
from bika.lims import bikaMessageFactory as _


class ClientLicenceTypesView(BikaListingView):
    """Displays all system's client licence types
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ClientLicenceTypesView, self).__init__(context, request)
        self.catalog = 'portal_catalog'
        self.contentFilter = {'portal_type': 'ClientLicenceType', 
                              'sort_on': 'sortable_title'}
        self.context_actions = {
            _('Add'):
                {'url': 'createObject?type_name=ClientLicenceType',
                'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Client Licence Types"))
        self.icon = "++resource++bika.lims.images/clientlicencetype_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Type'),
                      'index':'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         ]},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         ]},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description',
                         ]},
        ]

    def folderitem(self, obj, item, index):
        """
        Applies new properties to the item (ClientLicenceType) that is
        currently being rendered as a row in the list
        :param obj: clientlicencetype to be rendered as a row in the list
        :param item: dict representation of the unit, suitable for the list
        :param index: current position of the item within the list
        :type obj: DexterityContentType
        :type item: dict
        :type index: int
        :return: the dict representation of the item
        :rtype: dict
        """
        item['replace']['Title'] = "<a href='%s'>%s</a>" % \
             (item['url'], obj.Title())
        item['Description'] = obj.Description()
        return item


class ClientLicenceTypes(Container):
    implements(IClientLicenceTypes)
    displayContentsTab = False
