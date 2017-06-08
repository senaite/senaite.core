# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import ComputedField, StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import ComputedWidget, StringWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import AddressField
from bika.lims.browser.widgets import AddressWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaSchema

Salutation = StringField(
    'Salutation',
    storage=Storage(),
    widget=StringWidget(
        label=_("Salutation",
                "Title"),
        description=_("Greeting title eg. Mr, Mrs, Dr")
    ),
)

Firstname = StringField(
    'Firstname',
    storage=Storage(),
    required=1,
    widget=StringWidget(
        label=_("Firstname")
    ),
)

Middleinitial = StringField(
    'Middleinitial',
    storage=Storage(),
    required=0,
    widget=StringWidget(
        label=_("Middle initial")
    ),
)

Middlename = StringField(
    'Middlename',
    storage=Storage(),
    required=0,
    widget=StringWidget(
        label=_("Middle name")
    ),
)

Surname = StringField(
    'Surname',
    storage=Storage(),
    required=1,
    widget=StringWidget(
        label=_("Surname")
    ),
)

Fullname = ComputedField(
    'Fullname',
    storage=Storage(),
    expression='context.getFullname()',
    searchable=1,
    widget=ComputedWidget(
        label=_("Full Name"),
        visible={'edit': 'invisible', 'view': 'invisible'}
    ),
)

Username = StringField(
    'Username',
    storage=Storage(),
    widget=StringWidget(
        visible=False
    ),
)

EmailAddress = StringField(
    'EmailAddress',
    storage=Storage(),
    schemata='Email Telephone Fax',
    searchable=1,
    widget=StringWidget(
        label=_("Email Address")
    ),
)

BusinessPhone = StringField(
    'BusinessPhone',
    storage=Storage(),
    schemata='Email Telephone Fax',
    widget=StringWidget(
        label=_("Phone (business)")
    ),
)

BusinessFax = StringField(
    'BusinessFax',
    storage=Storage(),
    schemata='Email Telephone Fax',
    widget=StringWidget(
        label=_("Fax (business)")
    ),
)

HomePhone = StringField(
    'HomePhone',
    storage=Storage(),
    schemata='Email Telephone Fax',
    widget=StringWidget(
        label=_("Phone (home)")
    ),
)

MobilePhone = StringField(
    'MobilePhone',
    storage=Storage(),
    schemata='Email Telephone Fax',
    widget=StringWidget(
        label=_("Phone (mobile)")
    ),
)

JobTitle = StringField(
    'JobTitle',
    storage=Storage(),
    widget=StringWidget(
        label=_("Job title")
    ),
)

Department = StringField(
    'Department',
    storage=Storage(),
    widget=StringWidget(
        label=_("Department")
    ),
)

PhysicalAddress = AddressField(
    'PhysicalAddress',
    storage=Storage(),
    schemata='Address',
    widget=AddressWidget(
        label=_("Physical address")
    ),
)

City = ComputedField(
    'City',
    storage=Storage(),
    expression='context.getPhysicalAddress().get("city")',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    ),
)

District = ComputedField(
    'District',
    storage=Storage(),
    expression='context.getPhysicalAddress().get("district")',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    ),
)

PostalCode = ComputedField(
    'PostalCode',
    storage=Storage(),
    expression='context.getPhysicalAddress().get("postalCode")',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    ),
)

Country = ComputedField(
    'Country',
    storage=Storage(),
    expression='context.getPhysicalAddress().get("country")',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    ),
)

PostalAddress = AddressField(
    'PostalAddress',
    storage=Storage(),
    schemata='Address',
    widget=AddressWidget(
        label=_("Postal address")
    ),
)

ObjectWorkflowStates = ComputedField(
    'ObjectWorkflowStates',
    storage=Storage(),
    expression='context.getObjectWorkflowStates()',
    searchable=1,
    widget=ComputedWidget(
        visible=False
    ),
)

schema = BikaSchema.copy() + Schema((
    Salutation,
    Firstname,
    Middleinitial,
    Middlename,
    Surname,
    Fullname,
    Username,
    EmailAddress,
    BusinessPhone,
    BusinessFax,
    HomePhone,
    MobilePhone,
    JobTitle,
    Department,
    PhysicalAddress,
    City,
    District,
    PostalCode,
    Country,
    PostalAddress,
    ObjectWorkflowStates
))
