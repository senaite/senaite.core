# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import AddressField
from bika.lims.browser.widgets import AddressWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema, BikaSchema
from plone.app.folder.folder import ATFolder

Name = StringField(
    'Name',
    required=1,
    searchable=True,
    validators=('uniquefieldvalidator',),
    widget=StringWidget(
        label=_("Name")
    )
)
TaxNumber = StringField(
    'TaxNumber',
    widget=StringWidget(
        label=_("VAT number")
    )
)
Phone = StringField(
    'Phone',
    widget=StringWidget(
        label=_("Phone")
    )
)
Fax = StringField(
    'Fax',
    widget=StringWidget(
        label=_("Fax")
    )
)
EmailAddress = StringField(
    'EmailAddress',
    schemata='Address',
    widget=StringWidget(
        label=_("Email Address"),
    ),
    validators=('isEmail',)
)
PhysicalAddress = AddressField(
    'PhysicalAddress',
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
    schemata='Bank details',
    widget=StringWidget(
        label=_("Account Type")
    )
)
AccountName = StringField(
    'AccountName',
    schemata='Bank details',
    widget=StringWidget(
        label=_("Account Name")
    )
)
AccountNumber = StringField(
    'AccountNumber',
    schemata='Bank details',
    widget=StringWidget(
        label=_("Account Number")
    )
)
BankName = StringField(
    'BankName',
    schemata='Bank details',
    widget=StringWidget(
        label=_("Bank name")
    )
)
BankBranch = StringField(
    'BankBranch',
    schemata='Bank details',
    widget=StringWidget(
        label=_("Bank branch")
    )
)

schema = BikaFolderSchema.copy() + BikaSchema.copy() + ManagedSchema((
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


class Organisation(ATFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declareProtected(CMFCorePermissions.View, 'getSchema')

    def getSchema(self):
        return self.schema

    def Title(self):
        """ Return the Organisation's Name as its title """
        field = self.getField('Name')
        field = field and field.get(self) or ''
        return safe_unicode(field).encode('utf-8')

    def setTitle(self, value, **kwargs):
        return self.setName(value, **kwargs)

    def getPossibleAddresses(self):
        return ['PhysicalAddress', 'PostalAddress', 'BillingAddress']

    def getPrintAddress(self):
        postal = self.getPostalAddress()
        physical = self.getPhysicalAddress()
        billing = self.getBillingAddress()

        use_address = None
        if postal.get('city', False):
            use_address = postal
        elif physical.get('city', False):
            use_address = physical
        elif billing.get('city', False):
            use_address = billing

        address_lines = []
        if use_address:
            if use_address['address']:
                address_lines.append(use_address['address'])
            city_line = ''
            if use_address['city']:
                city_line += use_address['city'] + ' '
            if use_address['zip']:
                city_line += use_address['zip'] + ' '
            if city_line:
                address_lines.append(city_line)

            statecountry_line = ''
            if use_address['state']:
                statecountry_line += use_address['state'] + ', '
            if use_address['country']:
                statecountry_line += use_address['country']
            if statecountry_line:
                address_lines.append(statecountry_line)

        return address_lines


registerType(Organisation, PROJECTNAME)
