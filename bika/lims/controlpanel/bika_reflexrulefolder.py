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
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IReflexRuleFolder
from bika.lims.permissions import ManageBika, AddReflexRule
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from zope.interface.declarations import implements


class ReflexRuleFolderView(BikaListingView):

    def __init__(self, context, request):
        super(ReflexRuleFolderView, self).__init__(context, request)
        self.catalog = "portal_catalog"
        self.contentFilter = {
            'portal_type': 'ReflexRule',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0
            },
        }

        self.show_select_row = False
        self.show_select_column = True
        self.icon = self.portal_url +\
            "/++resource++bika.lims.images/reflexrule_big.png"
        self.title = self.context.translate(_("Reflex rules folder"))
        self.description = ""
        self.columns = {
            'Title': {
                'title': _('Reflex Rule'),
                'index': 'sortable_title'
            },
            'Method': {
                'title': _('Method'),
                'index': 'sortable_title'
            }
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'columns': ['Title', 'Method', ]},
            {'id': 'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
             'columns': ['Title', 'Method', ]},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['Title', 'Method', ]},
        ]

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission(
                permissions.ModifyPortalContent,
                self.context):
            self.context_actions[_('Add Reflex rule')] = {
                'url': 'createObject?type_name=ReflexRule',
                'permission': AddReflexRule,
                'icon': '++resource++bika.lims.images/add.png'
            }
        if not mtool.checkPermission(ManageBika, self.context):
            self.show_select_column = False
            self.review_states = [
                {'id': 'default',
                 'title': _('All'),
                 'contentFilter': {},
                 'columns': ['Title']}
            ]
        return super(ReflexRuleFolderView, self).__call__()

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        method = obj.getMethod()
        if method:
            item["Method"] = api.get_title(method)
            item["replace"]["Method"] = get_link_for(method)

        item["replace"]["Title"] = get_link(item["url"], item["Title"])
        return item


schema = ATFolderSchema.copy()


class ReflexRuleFolder(ATFolder):
    implements(IReflexRuleFolder)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(
    schema,
    folderish=True,
    moveDiscussion=False)

atapi.registerType(ReflexRuleFolder, PROJECTNAME)
