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
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import ILabProducts
from bika.lims.permissions import AddLabProduct
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

from bika.lims.utils import get_link


class LabProductsView(BikaListingView):

    def __init__(self, context, request):
        super(LabProductsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'LabProduct',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=LabProduct',
                                 'permission': AddLabProduct,
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Lab Products"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/product_big.png"
        self.description = ""

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title',
                      'toggle': True},
            'Volume': {'title': _('Volume'),
                       'toggle': True},
            'Unit': {'title': _('Unit'),
                       'toggle': True},
            'Price': {'title': _('Price'),
                       'index': 'price',
                       'toggle': True},
            'VATAmount': {'title': _('VAT Amount'),
                       'toggle': True},
            'TotalPrice': {'title': _('Total Price'),
                       'index': 'price_total',
                       'toggle': True},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Volume',
                         'Unit',
                         'Price',
                         'VATAmount',
                         'TotalPrice']},
            {'id':'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Volume',
                         'Unit',
                         'Price',
                         'VATAmount',
                         'TotalPrice']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Volume',
                         'Unit',
                         'Price',
                         'VATAmount',
                         'TotalPrice']},
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item.update({
            "Volume": obj.getVolume(),
            "Unit": obj.getUnit(),
            "Price": obj.getPrice(),
            "VATAmount": obj.getVATAmount(),
            "TotalPrice": obj.getTotalPrice(),
        })
        item["replace"]["Title"] = get_link(item["url"], value=item["Title"])
        return item


schema = ATFolderSchema.copy()
class LabProducts(ATFolder):
    implements(ILabProducts)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabProducts, PROJECTNAME)
