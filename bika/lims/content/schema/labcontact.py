# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""The lab staff
"""
import sys

from Products.Archetypes.public import ComputedField, ComputedWidget, \
    ImageField, ImageWidget, LinesField, MultiSelectionWidget, ReferenceField, \
    ReferenceWidget, Schema, SelectionWidget, StringField
from Products.Archetypes.references import HoldingReference
from bika.lims import bikaMessageFactory as _
from bika.lims.content.person import Person
from bika.lims.content.schema import Storage

PublicationPreference = LinesField(
    'PublicationPreference',
    storage=Storage,
    vocabulary_factory='bika.lims.vocabularies.CustomPubPrefVocabularyFactory',
    default='email',
    schemata='Publication preference',
    widget=MultiSelectionWidget(
        label=_("Publication preference")
    ),
)

Signature = ImageField(
    'Signature',
    storage=Storage,
    widget=ImageWidget(
        label=_("Signature"),
        description=_(
            "Upload a scanned signature to be used on printed analysis "
            "results reports. Ideal size is 250 pixels wide by 150 high")
    ),
)

# TODO: Department'll be delated
Department = ReferenceField(
    'Department',
    storage=Storage,
    required=0,
    vocabulary_display_path_bound=sys.maxint,
    allowed_types=('Department',),
    relationship='LabContactDepartment',
    vocabulary='getDepartments',
    referenceClass=HoldingReference,
    widget=ReferenceWidget(
        visible=False,
        checkbox_bound=0,
        label=_("Department"),
        description=_("The laboratory department")
    ),
)

DepartmentTitle = ComputedField(
    'DepartmentTitle',
    storage=Storage,
    expression="context.getDepartment().Title() "
               "if context.getDepartment() else ''",
    widget=ComputedWidget(
        visible=False,
    ),
)

Departments = ReferenceField(
    'Departments',
    storage=Storage,
    required=0,
    vocabulary_display_path_bound=sys.maxint,
    allowed_types=('Department',),
    relationship='LabContactDepartment',
    vocabulary='_departmentsVoc',
    referenceClass=HoldingReference,
    multiValued=1,
    widget=ReferenceWidget(
        checkbox_bound=0,
        label=_("Departments"),
        description=_("The laboratory departments")
    ),
)

DefaultDepartment = StringField(
    'DefaultDepartment',
    storage=Storage,
    required=0,
    vocabulary_display_path_bound=sys.maxint,
    vocabulary='_defaultDepsVoc',
    widget=SelectionWidget(
        visible=True,
        format='select',
        label=_("Default Department"),
        description=_("Default Department")
    ),
)

schema = Person.schema.copy() + Schema((
    PublicationPreference,
    Signature,
    Department,
    DepartmentTitle,
    Departments,
    DefaultDepartment
))

schema['JobTitle'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False
