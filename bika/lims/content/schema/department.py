# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from sys import maxint

from Products.Archetypes.Field import ComputedField, ReferenceField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

Manager = ReferenceField(
    'Manager',
    storage=Storage(),
    vocabulary='getContacts',
    vocabulary_display_path_bound=maxint,
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
    ),
)

ManagerName = ComputedField(
    'ManagerName',
    expression="context.getManager().getFullname() "
               "if context.getManager() else ''",
    widget=ComputedWidget(
        visible=False
    ),
)

ManagerPhone = ComputedField(
    'ManagerPhone',
    expression="context.getManager().getBusinessPhone() "
               "if context.getManager() else ''",
    widget=ComputedWidget(
        visible=False
    ),
)

ManagerEmail = ComputedField(
    'ManagerEmail',
    expression="context.getManager().getEmailAddress() "
               "if context.getManager() else ''",
    widget=ComputedWidget(
        visible=False
    ),
)

schema = BikaSchema.copy() + Schema((
    Manager,
    ManagerName,
    ManagerPhone,
    ManagerEmail
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'
