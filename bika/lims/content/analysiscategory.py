"""Analysis Category - the category of the analysis service

$Id: AnalysisCategory.py $
"""
import sys
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IAnalysisCategory
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims import bikaMessageFactory as _
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    ReferenceField('Department',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Department',),
        relationship = 'AnalysisCategoryDepartment',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _('Department'),
        ),
    ),
    ComputedField('DepartmentTitle',
        expression = "context.getDepartment() and context.getDepartment().Title() or ''",
        widget = ComputedWidget(
            visible = False,
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

registerType(AnalysisCategory, PROJECTNAME)
