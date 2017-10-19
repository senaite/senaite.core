# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""Analysis Category - the category of the analysis service
"""
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisCategory
from plone.indexer import indexer
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.interface import implements
import sys
import transaction
from bika.lims import deprecated


@indexer(IAnalysisCategory)
def sortable_title_with_sort_key(instance):
    sort_key = instance.getSortKey()
    if sort_key:
        return "{:010.3f}{}".format(sort_key, instance.Title())
    return instance.Title()


schema = BikaSchema.copy() + Schema((
    TextField('Comments',
        default_output_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget (
            description = _("To be displayed below each Analysis "
                            "Category section on results reports."),
            label = _("Comments")),
    ),
    # Department Field (as well as DepartmentTitle) of Analysis Category was removed.
    # It was a required field, but not used anywhere. When creating
    # an Analysis Request, we use Departments from 'Analysis Services'
    # instead.
    FloatField('SortKey',
        validators=('SortKeyValidator',),
        widget=DecimalWidget(
            label = _("Sort Key"),
            description = _("Float value from 0.0 - 1000.0 indicating the sort order. Duplicate values are ordered alphabetically."),
        ),
    ),
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
        for d in bsc(portal_type='Department',
                     inactive_state='active'):
            deps.append((d.UID, d.Title))
        return DisplayList(deps)

    def workflow_script_deactivat(self):
        # A instance cannot be deactivated if it contains services
        pu = getToolByName(self, 'plone_utils')
        bsc = getToolByName(self, 'bika_setup_catalog')
        ars = bsc(portal_type='AnalysisService', getCategoryUID=self.UID())
        if ars:
            message = _("Category cannot be deactivated because "
                        "it contains Analysis Services")
            pu.addPortalMessage(message, 'error')
            transaction.get().abort()
            raise WorkflowException

    @deprecated('[1.1] Returns None. Use departments from Analysis Services instead')
    def getDepartment(self):
        return None

    @deprecated('[1.1] Returns None. Use departments from Analysis Services instead')
    def getDepartmentTitle(self):
        return None

registerType(AnalysisCategory, PROJECTNAME)
