"""Department - the department in the laboratory.

$Id: Department.py 1000 2007-12-03 11:53:04Z anneline $
"""
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from AccessControl import ClassSecurityInfo
import sys
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    ReferenceField('Manager',
        vocabulary = 'getContactsDisplayList',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('LabContact',),
        referenceClass = HoldingReference,
        relationship = 'DepartmentLabContact',
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Manager"),
            description = _("Select a manager from the available personnel configured under the "
                            "'lab contacts' setup item. Departmental managers are referenced on "
                            "analysis results reports containing analyses by their department."),
        ),
    ),
    ComputedField('ManagerName',
        expression = "context.getManager() and context.getManager().getFullname() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ManagerPhone',
        expression = "context.getManager() and context.getManager().getBusinessPhone() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ManagerEmail',
        expression = "context.getManager() and context.getManager().getEmailAddress() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class Department(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        pairs = []
        for contact in bsc(portal_type = 'LabContact'):
            pairs.append((contact.UID, contact.Title))
        # sort the list by the second item
        pairs.sort(lambda x, y:cmp(x[1], y[1]))
        return DisplayList(pairs)

registerType(Department, PROJECTNAME)
