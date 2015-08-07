"""Analysis Category - the category of the analysis service
"""
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisCategory
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.interface import implements
import sys
import transaction

schema = BikaSchema.copy() + Schema((
    TextField('Comments',
        default_output_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget=TextAreaWidget (
            description = _("To be displayed below each Analysis "
                            "Category section on results reports."),
            label = _("Comments")),
    ),
    ReferenceField('Department',
        required=1,
        vocabulary='getDepartments',
        vocabulary_display_path_bound=sys.maxsize,
        allowed_types=('Department',),
        relationship='AnalysisCategoryDepartment',
        referenceClass=HoldingReference,
        widget=ReferenceWidget(
            checkbox_bound=0,
            label = _("Department"),
            description = _("The laboratory department"),
        ),
    ),
    ComputedField('DepartmentTitle',
        expression="context.getDepartment() and context.getDepartment().Title() or ''",
        widget=ComputedWidget(
            visible=False,
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


registerType(AnalysisCategory, PROJECTNAME)
