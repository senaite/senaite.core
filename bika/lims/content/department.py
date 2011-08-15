"""Department - the department in the laboratory.

$Id: Department.py 1000 2007-12-03 11:53:04Z anneline $
"""
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from AccessControl import ClassSecurityInfo
import sys

schema = BikaSchema.copy() + Schema((
    ReferenceField('Manager',
        vocabulary = 'getContactsDisplayList',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('LabContact',),
        referenceClass = HoldingReference,
        relationship = 'DepartmentLabContact',
    ),
    ComputedField('ManagerName',
        expression = 'here.getManagerName()',
        widget = ComputedWidget(
            label = 'Manager',
            visible = False,
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class Department(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        pairs = []
        for contact in self.portal_catalog(portal_type = 'LabContact'):
            pairs.append((contact.UID, contact.Title))
        # sort the list by the second item
        pairs.sort(lambda x, y:cmp(x[1], y[1]))
        return DisplayList(pairs)

    security.declarePublic('getManagerName')
    def getManagerName(self):
        if self.getManager():
            return self.getManager().getFullname()
        else:
            return ''

registerType(Department, PROJECTNAME)
