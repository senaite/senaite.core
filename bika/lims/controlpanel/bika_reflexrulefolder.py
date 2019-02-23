# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IReflexRuleFolder
from bika.lims.permissions import ManageBika
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
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
             'contentFilter': {'inactive_state': 'active'},
             'columns': ['Title', 'Method', ]},
            {'id': 'inactive',
             'title': _('Inactive'),
             'contentFilter': {'inactive_state': 'inactive'},
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

    # TODO use folderitem in develop!
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if 'obj' not in items[x]:
                continue
            obj = items[x]['obj']
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                (items[x]['url'], items[x]['Title'])
            method = items[x]['obj'].getMethod()
            items[x]['Method'] = method.title if method else ''
            items[x]['replace']['Method'] = "<a href='%s'>%s</a>" % \
                (method.absolute_url(), items[x]['Method']) if method else ''
        return items


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
