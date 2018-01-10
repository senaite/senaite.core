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
from bika.lims.interfaces import IAnalysisProfiles
from plone.app.folder.folder import ATFolderSchema, ATFolder
from zope.interface.declarations import implements
from zope.interface import alsoProvides


class AnalysisProfilesView(BikaSetupItemsView):

    def __init__(self, context, request):
        super(AnalysisProfilesView, self).__init__(
            context, request, 'AnalysisProfile', 'analysisprofile_big.png')
        self.title = self.context.translate(_("Analysis Profiles"))
        self.columns = {
            'Title': {
                'title': _('Profile'),
                'index': 'sortable_title',
                'replace_url': 'absolute_url'
            },
            'Description': {
                'title': _('Description'),
                'index': 'Description',
                'attr': 'Description'
            },
            'ProfileKey': {
                'title': _('Profile Key'),
                'attr': 'getProfileKey'
            },
        }
        for rs in self.review_states:
            rs['columns'] += ['ProfileKey']


schema = ATFolderSchema.copy()
class AnalysisProfiles(ATFolder):
    implements(IAnalysisProfiles)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(AnalysisProfiles, PROJECTNAME)
