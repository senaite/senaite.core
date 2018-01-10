# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.controlpanel.bika_instruments import InstrumentsView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from Products.CMFCore.utils import getToolByName
from bika.lims.utils import to_utf8
from Products.ATContentTypes.utils import DT2dt
from datetime import datetime

from bika.lims.browser.referencesample import ReferenceSamplesView

class SupplierInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(SupplierInstrumentsView, self).__init__(context, request)

    def isItemAllowed(self, obj):
        supp = obj.getRawSupplier() if obj else None
        return supp.UID() == self.context.UID() if supp else False


class SupplierReferenceSamplesView(ReferenceSamplesView):

    def __init__(self, context, request):
        super(SupplierReferenceSamplesView, self).__init__(context, request)
        self.contentFilter['path']['query'] = '/'.join(context.getPhysicalPath())
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=ReferenceSample',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        # Remove the Supplier column from the list
        del self.columns['Supplier']
        for rs in self.review_states:
            rs['columns'] = [col for col in rs['columns'] if col != 'Supplier']


class ContactsView(BikaListingView):

    def __init__(self, context, request):
        super(ContactsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'SupplierContact',
            'path': {"query": "/".join(context.getPhysicalPath()),
                     "level": 0}
        }
        self.context_actions = {_('Add'):
            {'url': 'createObject?type_name=SupplierContact',
             'icon': '++resource++bika.lims.images/add.png'}
        }
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.icon = self.portal_url + "/++resource++bika.lims.images/contact_big.png"
        self.title = self.context.translate(_("Contacts"))

        self.columns = {
            'getFullname': {'title': _('Full Name')},
            'getEmailAddress': {'title': _('Email Address')},
            'getBusinessPhone': {'title': _('Business Phone')},
            'getMobilePhone': {'title': _('Mobile Phone')},
            'getFax': {'title': _('Fax')},
        }

        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['getFullname',
                         'getEmailAddress',
                         'getBusinessPhone',
                         'getMobilePhone',
                         'getFax']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['getFullname'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['obj'].getFullname())

        return items
