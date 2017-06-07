# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""Department - the department in the laboratory.
"""
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from AccessControl import ClassSecurityInfo
import sys
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from zope.interface import implements
from bika.lims.interfaces import IDepartment

Manager = ReferenceField(
    'Manager',
    vocabulary='getContacts',
    vocabulary_display_path_bound=sys.maxint,
    allowed_types=('LabContact',),
    referenceClass=HoldingReference,
    relationship='DepartmentLabContact',
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Manager"),
        description=_(
            "Select a manager from the available personnel configured under "
            "the 'lab contacts' setup item. Departmental managers are "
            "referenced on analysis results reports containing analyses by "
            "their department.")
    )
)

ManagerName = ComputedField(
    'ManagerName',
    expression="context.getManager().getFullname() "
               "if context.getManager() else ''",
    widget=ComputedWidget(
        visible=False
    )
)

ManagerPhone = ComputedField(
    'ManagerPhone',
    expression="context.getManager().getBusinessPhone() "
               "if context.getManager() else ''",
    widget=ComputedWidget(
        visible=False
    )
)

ManagerEmail = ComputedField(
    'ManagerEmail',
    expression="context.getManager().getEmailAddress() "
               "if context.getManager() else ''",
    widget=ComputedWidget(
        visible=False
    )
)

schema = BikaSchema.copy() + Schema((
    Manager,
    ManagerName,
    ManagerPhone,
    ManagerEmail
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class Department(BaseContent):
    implements(IDepartment)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(Department, PROJECTNAME)
