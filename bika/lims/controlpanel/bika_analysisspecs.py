# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import IAnalysisSpecs
from zope.interface.declarations import implements
from plone.app.layout.globals.interfaces import IViewView

class AnalysisSpecsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AnalysisSpecsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'AnalysisSpec',
                              'path': {'query':"/".join(self.context.getPhysicalPath()),
                                       'level':0}}
        self.sort_on = 'Title'
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=AnalysisSpec',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.icon = self.portal_url + "/++resource++bika.lims.images/analysisspec_big.png"
        self.title = self.context.translate(_("Analysis Specifications"))
        self.description = self.context.translate(_(
            "Set up the laboratory analysis service results specifications"))
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'title',
                      'replace_url': 'absolute_url'},
            'SampleType': {'title': _('Sample Type'),
                           'index': 'getSampleTypeTitle',
                           'attr': 'getSampleType.Title',
                           'replace_url': 'getSampleType.absolute_url'},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title', 'SampleType']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title', 'SampleType']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title', 'SampleType']},
        ]


schema = ATFolderSchema.copy()
class AnalysisSpecs(ATFolder):
    implements(IAnalysisSpecs)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisSpecs, PROJECTNAME)
