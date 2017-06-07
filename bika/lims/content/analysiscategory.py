# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxsize

import transaction
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisCategory
from plone.indexer import indexer
from zope.interface import implements


@indexer(IAnalysisCategory)
def sortable_title_with_sort_key(instance):
    sort_key = instance.getSortKey()
    if sort_key:
        return "{:010.3f}{}".format(sort_key, instance.Title())
    return instance.Title()


Comments = TextField(
    'Comments',
    default_output_type='text/plain',
    allowable_content_types=('text/plain',),
    widget=TextAreaWidget(
        description=_(
            "To be displayed below each Analysis Category section on results "
            "reports."),
        label=_("Comments")),
)

Department = ReferenceField(
    'Department',
    required=1,
    vocabulary='getDepartments',
    vocabulary_display_path_bound=maxsize,
    allowed_types=('Department',),
    relationship='AnalysisCategoryDepartment',
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Department"),
        description=_("The laboratory department"),
    ),
)

SortKey = FloatField(
    'SortKey',
    validators=('SortKeyValidator',),
    widget=DecimalWidget(
        label=_("Sort Key"),
        description=_(
            "Float value from 0.0 - 1000.0 indicating the sort order. "
            "Duplicate values are ordered alphabetically."),
    ),
)

schema = BikaSchema.copy() + Schema((
    Comments,
    Department,
    SortKey,
))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'


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
