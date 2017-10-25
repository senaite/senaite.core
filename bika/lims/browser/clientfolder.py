# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import json

from zope.interface import implements
from zope.component import getUtility
from plone import protect
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.registry.interfaces import IRegistry

from bika.lims import api
from bika.lims import logger
from bika.lims.permissions import ManageAnalysisRequests
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.permissions import AddClient
from bika.lims.permissions import ManageClients
from bika.lims.browser import BrowserView


class ClientFolderContentsView(BikaListingView):
    """
    Listing view for all Clients
       """
    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(ClientFolderContentsView, self).__init__(context, request)
        self.contentFilter = {}
        self.icon = self.portal_url + "/++resource++bika.lims.images/client_big.png"
        self.title = self.context.translate(_("Clients"))
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 25
        request.set('disable_border', 1)

        self.columns = {
            'title': {'title': _('Name')},
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
        self.context_actions = {}
        mtool = api.get_tool(self.context, 'portal_membership')
        if mtool.checkPermission(AddClient, self.context):
            self.context_actions[_('Add')] = \
                {'url': 'createObject?type_name=Client',
                 'icon': '++resource++bika.lims.images/add.png'}
        if mtool.checkPermission(ManageClients, self.context):
            self.show_select_column = True
        return super(ClientFolderContentsView, self).__call__()

    def getClientList(self, contentFilter):
        searchTerm = self.request.get(self.form_id + '_filter', '').lower()
        mtool = api.get_tool('portal_membership')
        state = self.request.get('%s_review_state' % self.form_id,
                                 self.default_review_state)
        # This is used to decide how much of the objects need to be waked up
        # for further permission checks, which might get expensive on sites
        # with many clients
        list_pagesize = self.request.get("list_pagesize", self.pagesize)

        states = {
            'default': ['active', ],
            'active': ['active', ],
            'inactive': ['inactive', ],
            'all': ['active', 'inactive']
        }

        # Use the catalog to speed things up and also limit the results
        catalog = api.get_tool("portal_catalog")
        catalog_query = {
            "portal_type": "Client",
            "inactive_state": states[state],
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        # Inject the searchTerm to narrow the results further
        if searchTerm:
            catalog_query["SearchableText"] = searchTerm
        logger.debug("getClientList::catalog_query=%s" % catalog_query)
        brains = catalog(catalog_query)

        clients = []
        for brain in brains:
            # only wake up objects if they are shown on one page
            if len(clients) > list_pagesize:
                # otherwise append only the brain
                clients.append(brain)
                continue

            # wake up the object
            client = brain.getObject()
            # skip clients where the search term does not match
            if searchTerm and not client_match(client, searchTerm):
                continue
            # Only show clients to which we have Manage AR rights.
            # (ritamo only sees Happy Hills).
            if not mtool.checkPermission(ManageAnalysisRequests, client):
                continue
            clients.append(brain)

        return clients

    def folderitems(self):
        self.contentsMethod = self.getClientList
        items = BikaListingView.folderitems(self)
        registry = getUtility(IRegistry)
        if 'bika.lims.client.default_landing_page' in registry:
            landing_page = registry['bika.lims.client.default_landing_page']
        else:
            landing_page = 'analysisrequests'

        for item in items:
            if "obj" not in item:
                continue
            obj = item['obj']

            item['replace']['title'] = "<a href='%s/%s'>%s</a>" % \
                (item['url'], landing_page.encode('ascii'), item['title'])

            item['EmailAddress'] = obj.getEmailAddress()
            item['replace']['EmailAddress'] = "<a href='%s'>%s</a>" % \
                ('mailto:%s' % obj.getEmailAddress(), obj.getEmailAddress())
            item['Phone'] = obj.getPhone()
            item['Fax'] = obj.getFax()
            item['ClientID'] = obj.getClientID()

        return items


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
               'rows': rows[(int(page) - 1) * int(nr_rows): int(page) * int(nr_rows)]}

        return json.dumps(ret)
