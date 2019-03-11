# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import ISamplingRoundTemplates
from bika.lims.permissions import AddSRTemplate
from bika.lims.utils import checkPermissions
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import ModifyPortalContent
from zope.interface.declarations import implements


class SamplingRoundTemplatesView(BikaListingView):
    """
    Displays the list of Sampling Round Templates registered in the system.
    For users with 'Bika: Add SRTemplate' permission granted (along with
    ModifyPortalContent and AddPortalContent), an "Add" button will be
    displayed at the top of the list.
    """

    def __init__(self, context, request):
        super(SamplingRoundTemplatesView, self).__init__(context, request)
        self.form_id = "srtemplates"
        self.show_select_column = True
        self.icon = self.portal_url + "/++resource++bika.lims.images/srtemplate_big.png"
        self.title = self.context.translate(_("Sampling Round Templates"))
        self.catalog = "bika_setup_catalog"
        self.contentFilter = {
            'portal_type': 'SRTemplate',
            'sort_order': 'sortable_title',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0
            },
        }
        self.columns = {
            'Title': {
                'title': _('Template'),
                'index': 'sortable_title',
                'replace_url': 'absolute_url'
            },
            'Description': {
                'title': _('Description'),
                'index': 'description'
            },
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'is_active': True},
             'columns': ['Title',
                         'Description']},
            {'id':'inactive',
             'title': _('Inactive'),
             'contentFilter': {'is_active': False},
             'columns': ['Title',
                         'Description']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description']},
        ]

    def __call__(self):
        # Has the current user (might be a Client's contact) enough
        # privileges to add a Sampling Round Template?. This check must be done
        # here in the __call__ function because the user (and checkpermission)
        # is only accessible once the object has already been instantiated.
        reqperms = [ModifyPortalContent, AddPortalContent, AddSRTemplate]
        if checkPermissions(reqperms, self.context):
            self.context_actions = {
                _('Add'): {
                    'url': 'createObject?type_name=SRTemplate',
                    'permission': AddSRTemplate,
                    'icon': '++resource++bika.lims.images/add.png'
                }
            }
        return super(SamplingRoundTemplatesView, self).__call__()

    def before_render(self):
        """Before template render hook
        """
        # Don't allow any context actions
        self.request.set("disable_border", 1)


schema = ATFolderSchema.copy()


class SRTemplates(ATFolder):
    implements(ISamplingRoundTemplates)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(SRTemplates, PROJECTNAME)
