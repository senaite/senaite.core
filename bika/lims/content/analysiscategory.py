# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

import transaction
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.analysiscategory import schema
from bika.lims.interfaces import IAnalysisCategory
from plone.indexer import indexer
from zope.interface import implements


@indexer(IAnalysisCategory)
def sortable_title_with_sort_key(instance):
    sort_key = instance.getSortKey()
    if sort_key:
        return "{:010.3f}{}".format(sort_key, instance.Title())
    return instance.Title()


class AnalysisCategory(BaseContent):
    implements(IAnalysisCategory)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getDepartments(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        deps = []
        for d in bsc(portal_type='Department', inactive_state='active'):
            deps.append((d.UID, d.Title))
        return DisplayList(deps)

    def workflow_script_deactivat(self):
        # A instance cannot be deactivated if it contains services
        pu = getToolByName(self, 'plone_utils')
        bsc = getToolByName(self, 'bika_setup_catalog')
        ars = bsc(portal_type='AnalysisService', getCategoryUID=self.UID())
        if ars:
            message = _(
                "Category cannot be deactivated because it contains Analysis "
                "Services")
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException

    def getDepartmentTitle(self):
        """Populates catalog index and metadata column.
        """
        department = self.getDepartment()
        if department:
            return department.Title()
        return ''


registerType(AnalysisCategory, PROJECTNAME)
