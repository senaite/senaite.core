# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import AddClient
from bika.lims.permissions import ManageAnalysisRequests
from bika.lims.permissions import ManageClients
from bika.lims.utils import get_email_link, get_link, get_registry_value, \
    check_permission
from plone import protect
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements


class ClientFolderContentsView(BikaListingView):
    """
    Listing view for all Clients
       """
    implements(IFolderContentsView)

    _LANDING_PAGE_REGISTRY_KEY = "bika.lims.client.default_landing_page"
    _DEFAULT_LANDING_PAGE = "analysisrequests"

    def __init__(self, context, request):
        super(ClientFolderContentsView, self).__init__(context, request)

        self.title = self.context.translate(_("Clients"))
        self.description = ""
        self.form_id = "list_clientsfolder"
        self.sort_on = "sortable_title"
        # Landing page to be added to the link of each client from the list
        self.landing_page = get_registry_value(self._LANDING_PAGE_REGISTRY_KEY,
                                               self._DEFAULT_LANDING_PAGE)
        self.contentFilter = {'portal_type': 'Client',
                              'sort_on': 'sortable_title',
                              'sort_order': 'ascending'}

        self.filter_indexes = ['title', 'SearchableText']

        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 25
        self.icon = '{}/{}'.\
            format(self.portal_url,
            "++resource++bika.lims.images/client_big.png")
        request.set('disable_border', 1)

        self.columns = {
            'title': {'title': _('Name'), 'index': 'sortable_title'},
            'EmailAddress': {'title': _('Email Address')},
            'getCountry': {'title': _('Country')},
            'getProvince': {'title': _('Province')},
            'getDistrict': {'title': _('District')},
            'Phone': {'title': _('Phone')},
            'Fax': {'title': _('Fax')},
            'ClientID': {'title': _('Client ID')},
            'BulkDiscount': {'title': _('Bulk Discount')},
            'MemberDiscountApplies': {'title': _('Member Discount')},
        }

        self.review_states = [  # leave these titles and ids alone
            {'id': 'default',
             'contentFilter': {'inactive_state': 'active'},
             'title': _('Active'),
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['title',
                         'ClientID',
                         'getCountry',
                         'getProvince',
                         'getDistrict',
                         'EmailAddress',
                         'Phone',
                         'Fax', ]
             },
            {'id': 'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id': 'activate'}, ],
             'columns': ['title',
                         'ClientID',
                         'getCountry',
                         'getProvince',
                         'getDistrict',
                         'EmailAddress',
                         'Phone',
                         'Fax', ]
             },
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [],
             'columns': ['title',
                         'ClientID',
                         'getCountry',
                         'getProvince',
                         'getDistrict',
                         'EmailAddress',
                         'Phone',
                         'Fax', ]
             },
        ]

    def __call__(self):
        if check_permission(AddClient, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=Client',
                 'icon': '++resource++bika.lims.images/add.png'}

        # Display a checkbox next to each client in the list only if the user
        # has rights for ManageClients
        self.show_select_column = check_permission(ManageClients, self.context)

        return super(ClientFolderContentsView, self).__call__()

    def isItemAllowed(self, obj):
        """
        Returns true if the current user has Manage AR rights for the current
        Client (item) to be rendered.
        :param obj: client to be rendered as a row in the list
        :type obj: ATContentType/DexterityContentType
        :return: True if the current user can see this Client. Otherwise, False.
        :rtype: bool
        """
        return check_permission(ManageAnalysisRequests, obj)

    def folderitem(self, obj, item, index):
        """
        Applies new properties to the item (Client) that is currently being
        rendered as a row in the list
        :param obj: client to be rendered as a row in the list
        :param item: dict representation of the client, suitable for the list
        :param index: current position of the item within the list
        :type obj: ATContentType/DexterityContentType
        :type item: dict
        :type index: int
        :return: the dict representation of the item
        :rtype: dict
        """
        link_url = "{}/{}".format(item['url'], self.landing_page)
        item['replace']['title'] = get_link(link_url, item['title'])
        item['replace']['EmailAddress'] = get_email_link(item['EmailAddress'])
        return item


def client_match(client, search_term):
    # Check if the search_term matches some common fields
    if search_term in client.getClientID().lower():
        return True
    if search_term in client.Title().lower():
        return True
    if search_term in client.getName().lower():
        return True
    if search_term in client.Description().lower():
        return True
    return False


class ajaxGetClients(BrowserView):
    """Vocabulary source for jquery combo dropdown box
    """

    def __call__(self):
        protect.CheckAuthenticator(self.request)
        searchTerm = self.request.get('searchTerm', '').lower()
        page = self.request.get('page', 1)
        nr_rows = self.request.get('rows', 20)
        sort_order = self.request.get('sord') or 'ascending'
        sort_index = self.request.get('sidx') or 'sortable_title'

        if sort_order == "desc":
            sort_order = "descending"

        # Use the catalog to speed things up and also limit the results
        catalog = api.get_tool("portal_catalog")
        catalog_query = {
            "portal_type": "Client",
            "inactive_state": "active",
            "sort_on": sort_index,
            "sort_order": sort_order,
            "sort_limit": 500
        }
        # Inject the searchTerm to narrow the results further
        if searchTerm:
            catalog_query["SearchableText"] = searchTerm
        logger.debug("ajaxGetClients::catalog_query=%s" % catalog_query)
        brains = catalog(catalog_query)
        rows = []

        for brain in brains:
            client = brain.getObject()
            # skip clients where the search term does not match
            if searchTerm and not client_match(client, searchTerm):
                continue
            rows.append(
                {
                    "ClientID": client.getClientID(),
                    "Title": client.Title(),
                    "ClientUID": client.UID(),
                }
            )

        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[(int(page) - 1) * int(nr_rows):
                             int(page) * int(nr_rows)]}

        return json.dumps(ret)
