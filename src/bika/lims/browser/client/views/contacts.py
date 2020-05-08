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

from collections import OrderedDict

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.interfaces import IContacts
from bika.lims.utils import get_link, get_email_link
from bika.lims.vocabularies import CatalogVocabulary
from zope.interface import implements


class ClientContactsView(BikaListingView):
    implements(IContacts)

    def __init__(self, context, request):
        super(ClientContactsView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'Contact',
            'sort_on': 'sortable_title',
            'path': {
                "query": "/".join(context.getPhysicalPath()),
                "level": 0
            }
        }
        self.context_actions = {
            _('Add'):
                {'url': 'createObject?type_name=Contact',
                 'permission': 'Add portal content',
                 'icon': '++resource++bika.lims.images/add.png'}}

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50
        self.form_id = "contacts"

        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/client_contact_big.png"
        self.title = self.context.translate(_("Contacts"))
        self.description = ""

        self.columns = OrderedDict((
            ("getFullname", {
                "title": _("Full Name"),
                "index": "getFullname",
                "sortable": True, }),
            ("Username", {
                "title": _("User Name"), }),
            ("getEmailAddress", {
                "title": _("Email Address"), }),
            ("getBusinessPhone", {
                "title": _("Business Phone"), }),
            ("getMobilePhone", {
                "title": _("MobilePhone"), }),
        ))

        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': self.columns.keys()},
            {'id': 'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
             'transitions': [{'id': 'activate'}, ],
             'columns': self.columns.keys()},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': self.columns.keys()},
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        url = item.get("url")
        email = obj.getEmailAddress()
        fullname = obj.getFullname()
        item['getFullname'] = fullname
        item['getEmailAddress'] = email
        item['getBusinessPhone'] = obj.getBusinessPhone()
        item['getMobilePhone'] = obj.getMobilePhone()
        item['Username'] = obj.getUsername() or ""
        item['replace']['getFullname'] = get_link(url, fullname)
        if email:
            item["replace"]['getEmailAddress'] = get_email_link(email)
        return item


class ClientContactVocabularyFactory(CatalogVocabulary):
    def __call__(self):
        return super(ClientContactVocabularyFactory, self).__call__(
            portal_type='Contact',
            path={'query': "/".join(self.context.getPhysicalPath()),
                  'level': 0}
        )
