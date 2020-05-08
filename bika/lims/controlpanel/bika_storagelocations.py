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

import json

import plone
from Products.ATContentTypes.content import schemata
from Products.Archetypes import PloneMessageFactory as _p
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IStorageLocations
from bika.lims.permissions import AddStorageLocation
from bika.lims.utils import get_link
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from zope.interface.declarations import implements

from bika.lims.utils import get_link


class StorageLocationsView(BikaListingView):

    def __init__(self, context, request):
        super(StorageLocationsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'StorageLocation',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                            {'url': 'createObject?type_name=StorageLocation',
                             'permission': AddStorageLocation,
                             'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Storage Locations"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/storagelocation_big.png"
        self.description = ""

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Storage Location'),
                      'index':'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'SiteTitle': {'title': _p('Site Title'),
                      'toggle': True},
            'SiteCode': {'title': _p('Site Code'),
                      'toggle': True},
            'LocationTitle': {'title': _p('Location Title'),
                      'toggle': True},
            'LocationCode': {'title': _p('Location Code'),
                      'toggle': True},
            'ShelfTitle': {'title': _p('Shelf Title'),
                      'toggle': True},
            'ShelfCode': {'title': _p('Shelf Code'),
                      'toggle': True},
            'Owner': {'title': _p('Owner'),
                      'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title', 'Description', 'Owner',  'SiteTitle', 'SiteCode', 'LocationTitle', 'LocationCode', 'ShelfTitle', 'ShelfCode']},
            {'id':'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title', 'Description', 'Owner', 'SiteTitle', 'SiteCodeShelfCode' ]},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title', 'Description', 'Owner', 'SiteTitle', 'SiteCodeShelfCode' ]},
        ]

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["Description"] = obj.Description()
        item["replace"]["Title"] = get_link(item["url"], item["Title"])

        parent = api.get_parent(obj)
        if IClient.providedBy(parent):
            item["Owner"] = api.get_title(parent)
        else:
            item["Owner"] = self.context.bika_setup.laboratory.Title()
        return item


schema = ATFolderSchema.copy()


class StorageLocations(ATFolder):
    implements(IStorageLocations)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(StorageLocations, PROJECTNAME)


class ajax_StorageLocations(BrowserView):
    """ The autocomplete data source for storage location selection widgets.
        Returns a JSON list of storage location titles.

        Request parameters:

        - term: the string which will be searched against all Storage Location
          titles.

        - _authenticator: The plone.protect authenticator.

    """

    def filter_list(self, items, searchterm):
        if searchterm and len(searchterm) < 3:
            # Items that start with A or AA
            res = [s.getObject()
                     for s in items
                     if s.title.lower().startswith(searchterm)]
            if not res:
                # or, items that contain A or AA
                res = [s.getObject()
                         for s in items
                         if s.title.lower().find(searchterm) > -1]
        else:
            # or, items that contain searchterm.
            res = [s.getObject()
                     for s in items
                     if s.title.lower().find(searchterm) > -1]
        return res

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        term = safe_unicode(self.request.get('term', '')).lower()
        if not term:
            return json.dumps([])

        client_items = lab_items = []

        # User (client) storage locations
        if self.context.portal_type == 'Client':
            client_path = self.context.getPhysicalPath()
            client_items = list(
                bsc(portal_type = "StorageLocation",
                    path = {"query": "/".join(client_path), "level" : 0 },
                    is_active = True,
                    sort_on='sortable_title'))

        # Global (lab) storage locations
        lab_path = \
                self.context.bika_setup.bika_storagelocations.getPhysicalPath()
        lab_items = list(
            bsc(portal_type = "StorageLocation",
                path = {"query": "/".join(lab_path), "level" : 0 },
                is_active = True,
                sort_on='sortable_title'))

        client_items = [callable(s.Title) and s.Title() or s.title
                 for s in self.filter_list(client_items, term)]
        lab_items = [callable(s.Title) and s.Title() or s.title
                 for s in self.filter_list(lab_items, term)]
        lab_items = ["%s: %s" % (_("Lab"), safe_unicode(i))
                     for i in lab_items]

        items = client_items + lab_items

        return json.dumps(items)
