# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IUnitConversions
from bika.lims.browser.bika_listing import BikaListingView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from plone.dexterity.content import Container
from zope.interface import implements


class UnitConversionsView(BikaListingView):
    """Displays all system's unit conversions
    """
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(UnitConversionsView, self).__init__(context, request)
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {'portal_type': 'UnitConversion',
                              'sort_on': 'sortable_title'}
        self.context_actions = \
            {_('Add'):
                {'url': '++add++UnitConversion',
                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Unit Conversions"))
        self.icon = self.portal_url + \
            "/++resource++bika.lims.images/analysisspec_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = "unitconversion"

        self.columns = {
            'Unit': {'title': _('Unit'),
                     'index': 'title'},
            'Converted Unit':
                {'title': _('Converted Unit'),
                 'index': 'converted_unit',
                 'toggle': True},
            'Formula': {'title': _('Formula'),
                        'index': 'formula',
                        'toggle': True},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
        }

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['Unit',
                         'Converted Unit',
                         'Formula',
                         'Description',
                         ]},
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['Unit',
                         'Converted Unit',
                         'Formula',
                         'Description',
                         ]},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Unit',
                         'Converted Unit',
                         'Formula',
                         'Description',
                         ]},
        ]

    def folderitem(self, obj, item, index):
        """
        Applies new properties to the item (UnitConversion) that is currently
        being rendered as a row in the list
        :param obj: unit conversion to be rendered as a row in the list
        :param item: dict representation of the unit, suitable for the list
        :param index: current position of the item within the list
        :type obj: DexterityContentType
        :type item: dict
        :type index: int
        :return: the dict representation of the item
        :rtype: dict
        """
        item['Unit'] = obj.title
        item['replace']['Unit'] = "<a href='%s' title='%s'>%s</a>" % \
            (item['url'], item['url_href_title'], item['Unit'])
        item['Converted Unit'] = obj.converted_unit
        item['Formula'] = obj.formula
        item['Description'] = obj.Description()
        return item


class UnitConversions(Container):
    implements(IUnitConversions)
    displayContentsTab = False
