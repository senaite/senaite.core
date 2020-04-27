# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import ManagedSchema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import registerType
from Products.CMFPlone.utils import safe_unicode
from plone.app.folder.folder import ATFolder
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import AddressField
from bika.lims.browser.widgets import AddressWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IOrganisation

schema = BikaFolderSchema.copy() + BikaSchema.copy() + ManagedSchema((

    StringField(
        "Name",
        required=1,
        searchable=True,
        widget=StringWidget(
            label=_("Name"),
        ),
    ),

    StringField(
        "TaxNumber",
        widget=StringWidget(
            label=_("VAT number"),
        ),
    ),

    StringField(
        "Phone",
        widget=StringWidget(
            label=_("Phone"),
        ),
    ),

    StringField(
        "Fax",
        widget=StringWidget(
            label=_("Fax"),
        ),
    ),

    StringField(
        "EmailAddress",
        schemata="Address",
        widget=StringWidget(
            label=_("Email Address"),
        ),
        validators=("isEmail", )
    ),

    AddressField(
        "PhysicalAddress",
        schemata="Address",
        widget=AddressWidget(
            label=_("Physical address"),
        ),
        subfield_validators={
            "country": "inline_field_validator",
            "state": "inline_field_validator",
            "district": "inline_field_validator",
        },
    ),

    AddressField(
        "PostalAddress",
        schemata="Address",
        widget=AddressWidget(
            label=_("Postal address"),
        ),
        subfield_validators={
            "country": "inline_field_validator",
            "state": "inline_field_validator",
            "district": "inline_field_validator",
        },
    ),

    AddressField(
        "BillingAddress",
        schemata="Address",
        widget=AddressWidget(
            label=_("Billing address"),
        ),
        subfield_validators={
            "country": "inline_field_validator",
            "state": "inline_field_validator",
            "district": "inline_field_validator",
        },
    ),

    StringField(
        "AccountType",
        schemata="Bank details",
        widget=StringWidget(
            label=_("Account Type"),
        ),
    ),

    StringField(
        "AccountName",
        schemata="Bank details",
        widget=StringWidget(
            label=_("Account Name"),
        ),
    ),

    StringField(
        "AccountNumber",
        schemata="Bank details",
        widget=StringWidget(
            label=_("Account Number"),
        ),
    ),

    StringField(
        "BankName",
        schemata="Bank details",
        widget=StringWidget(
            label=_("Bank name"),
        ),
    ),

    StringField(
        "BankBranch",
        schemata="Bank details",
        widget=StringWidget(
            label=_("Bank branch"),
        ),
    ),
),
)

IdField = schema["id"]
IdField.widget.visible = {"edit": "visible", "view": "invisible"}

TitleField = schema["title"]
TitleField.required = 0
TitleField.widget.visible = {"edit": "hidden", "view": "invisible"}


class Organisation(ATFolder):
    """Base class for Clients, Suppliers and for the Laboratory
    """
    implements(IOrganisation)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def Title(self):
        """Return the name of the Organisation
        """
        field = self.getField("Name")
        field = field and field.get(self) or ""
        return safe_unicode(field).encode("utf-8")

    def setTitle(self, value):
        """Set the name of the Organisation
        """
        return self.setName(value)

    def getPossibleAddresses(self):
        """Get the possible address fields
        """
        return ["PhysicalAddress", "PostalAddress", "BillingAddress"]

    def getPrintAddress(self):
        """Get an address for printing
        """
        address_lines = []

        addresses = [
            self.getPostalAddress(),
            self.getPhysicalAddress(),
            self.getBillingAddress(),
        ]

        for address in addresses:
            city = address.get("city", "")
            zip = address.get("zip", "")
            state = address.get("state", "")
            country = address.get("country", "")

            if city:
                address_lines = [
                    address["address"].strip(),
                    "{} {}".format(city, zip).strip(),
                    "{} {}".format(state, country).strip(),
                ]
                break

        return address_lines


registerType(Organisation, PROJECTNAME)
