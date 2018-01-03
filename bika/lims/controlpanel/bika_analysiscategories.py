# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from bika.lims.controlpanel.bika_setupitems import BikaSetupItemsView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IAnalysisCategories
from plone.app.folder.folder import ATFolderSchema, ATFolder
from zope.interface.declarations import implements
from zope.interface import alsoProvides


class AnalysisCategoriesView(BikaSetupItemsView):

    def __init__(self, context, request):
        super(AnalysisCategoriesView, self).__init__(
            context, request, 'AnalysisCategory', 'category_big.png')
        self.title = self.context.translate(_("Analysis Categories"))
        self.columns = {
            'Title': {
                'title': _('Category'),
                'index': 'sortable_title',
                'replace_url': 'absolute_url'
            },
            'Description': {
                'title': _('Description'),
                'index': 'description',
                'attr': 'Description',
                'toggle': False
            },
            'Department': {
                'title': _('Department'),
                'index': 'getDepartmentTitle',
                'attr': 'getDepartmentTitle',
            },
            'SortKey': {
                'title': _('Sort Key'),
                'attr': 'getSortKey',
                'sortable': False
            },
        }
        for rs in self.review_states:
            rs['columns'] += ['Department', 'SortKey']


schema = ATFolderSchema.copy()
class AnalysisCategories(ATFolder):
    implements(IAnalysisCategories)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(AnalysisCategories, PROJECTNAME)
