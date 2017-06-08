# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import StringWidget
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import AddressField
from bika.lims.browser.widgets import AddressWidget
from bika.lims.content.schema import Storage
from bika.lims.content.schema.bikaschema import BikaFolderSchema, BikaSchema

Name = StringField(
    'Name',
    storage=Storage(),
    required=1,
    searchable=True,
    validators=('uniquefieldvalidator',),
    widget=StringWidget(
        label=_("Name")
    ),
)

TaxNumber = StringField(
    'TaxNumber',
    storage=Storage(),
    widget=StringWidget(
        label=_("VAT number")
    ),
)

Phone = StringField(
    'Phone',
    storage=Storage(),
    widget=StringWidget(
        label=_("Phone")
    ),
)

Fax = StringField(
    'Fax',
    storage=Storage(),
    widget=StringWidget(
        label=_("Fax")
    ),
)

EmailAddress = StringField(
    'EmailAddress',
    storage=Storage(),
    schemata='Address',
    widget=StringWidget(
        label=_("Email Address"),
    ),
    validators=('isEmail',),
)

PhysicalAddress = AddressField(
    'PhysicalAddress',
    storage=Storage(),
    schemata='Address',
    widget=AddressWidget(
        label=_("Physical address"),
    ),
    subfield_validators={
        'country': 'inline_field_validator',
        'state': 'inline_field_validator',
        'district': 'inline_field_validator',
    },
    inline_field_validator="validate_address"
)
PostalAddress = AddressField(
    'PostalAddress',
    storage=Storage(),
    schemata='Address',
    widget=AddressWidget(
        label=_("Postal address"),
    ),
    subfield_validators={
        'country': 'inline_field_validator',
        'state': 'inline_field_validator',
        'district': 'inline_field_validator',
    },
    inline_field_validator="validate_address"
)
BillingAddress = AddressField(
    'BillingAddress',
    storage=Storage(),
    schemata='Address',
    widget=AddressWidget(
        label=_("Billing address"),
    ),
    subfield_validators={
        'country': 'inline_field_validator',
        'state': 'inline_field_validator',
        'district': 'inline_field_validator',
    },
    inline_field_validator="validate_address"
)
AccountType = StringField(
    'AccountType',
    storage=Storage(),
    schemata='Bank details',
    widget=StringWidget(
        label=_("Account Type")
    ),
)

AccountName = StringField(
    'AccountName',
    storage=Storage(),
    schemata='Bank details',
    widget=StringWidget(
        label=_("Account Name")
    ),
)

AccountNumber = StringField(
    'AccountNumber',
    storage=Storage(),
    schemata='Bank details',
    widget=StringWidget(
        label=_("Account Number")
    ),
)

BankName = StringField(
    'BankName',
    storage=Storage(),
    schemata='Bank details',
    widget=StringWidget(
        label=_("Bank name")
    ),
)

BankBranch = StringField(
    'BankBranch',
    storage=Storage(),
    schemata='Bank details',
    widget=StringWidget(
        label=_("Bank branch")
    ),
)

schema = BikaFolderSchema.copy() + BikaSchema.copy() + Schema((
    Name,
    TaxNumber,
    Phone,
    Fax,
    EmailAddress,
    PhysicalAddress,
    PostalAddress,
    BillingAddress,
    AccountType,
    AccountName,
    AccountNumber,
    BankName,
    BankBranch
))

IdField = schema['id']
IdField.widget.visible = {'edit': 'visible', 'view': 'invisible'}
# Don't make title required - it will be computed from the Organisation's
# Name
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}
