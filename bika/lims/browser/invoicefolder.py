# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.
from Products.CMFCore.permissions import ModifyPortalContent
from bika.lims import bikaMessageFactory as _
from bika.lims import api
from bika.lims.utils import t
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import AddInvoice
from bika.lims.permissions import ManageInvoices
from plone.app.content.browser.interfaces import IFolderContentsView
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


class InvoiceFolderContentsView(BikaListingView):

    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(InvoiceFolderContentsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {'portal_type': 'InvoiceBatch'}
        self.icon = self.portal_url + "/++resource++bika.lims.images/invoice_big.png"
        self.title = self.context.translate(_("Statements"))
        self.description = ""

        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 25
        request.set('disable_border', 1)
        self.columns = {
            'title': {'title': _('Title')},
            'start': {'title': _('Start Date')},
            'end': {'title': _('End Date')},
        }
        self.review_states = [
            {
                'id': 'default',
                'contentFilter': {'is_active': True},
                'title': _('Active'),
                'transitions': [{'id': 'cancel'}],
                'columns': ['title', 'start', 'end'],
            },
            {
                'id': 'cancelled',
                'contentFilter': {'is_active': False},
                'title': _('Cancelled'),
                'transitions': [{'id': 'reinstate'}],
                'columns': ['title', 'start', 'end'],
            },
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if (mtool.checkPermission(AddInvoice, self.context)):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=InvoiceBatch',
                'icon': '++resource++bika.lims.images/add.png'
            }
        if mtool.checkPermission(ModifyPortalContent, self.context):
            self.show_select_column = True
        return super(InvoiceFolderContentsView, self).__call__()

    def getInvoiceBatches(self, contentFilter={}):
        wf = getToolByName(self.context, 'portal_workflow')
        active_state = contentFilter.get('is_active', True)
        values = self.context.objectValues()
        if active_state:
            return filter(api.is_active, values)
        else:
            return filter(lambda o: not api.is_active(o), values)

    def folderitems(self):
        self.contentsMethod = self.getInvoiceBatches
        items = BikaListingView.folderitems(self)
        for x, item in enumerate(items):
            if 'obj' not in item:
                continue
            obj = item['obj']
            title_link = "<a href='%s'>%s</a>" % (item['url'], item['title'])
            items[x]['replace']['title'] = title_link
            items[x]['start'] = self.ulocalized_time(obj.getBatchStartDate())
            items[x]['end'] = self.ulocalized_time(obj.getBatchEndDate())

        return items
