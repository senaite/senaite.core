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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import senaiteMessageFactory as _
from senaite.core.schema import AddressField
from senaite.core.z3cform.widgets.address import AddressWidget
from senaite.core.content.base import Container
from plone.supermodel import model
from plone.schema.email import Email
from plone.autoform import directives
from Products.CMFCore import permissions
from Products.CMFPlone.utils import safe_unicode
from zope import schema
from zope.interface import implementer


class IOrganizationSchema(model.Schema):
    """Base schema for Supplier schema and etc.
    """

    name = schema.TextLine(
        title=_(
            "title_organization_name",
            default="Name"
        ),
        required=True,
    )

    tax_number = schema.TextLine(
        title=_(
            "title_organization_tax_number",
            default="VAT number"
        ),
        required=False,
    )

    phone = schema.TextLine(
        title=_(
            "title_organization_phone",
            default="Phone"
        ),
        required=False,
    )

    fax = schema.TextLine(
        title=_(
            "title_organization_fax",
            default="Fax"
        ),
        required=False,
    )

    model.fieldset(
        "addresses",
        label=_(
            "title_addresses_tab",
            default="Address"
        ),
        fields=[
            "email_address",
            "physical_address",
            "postal_address",
            "billing_address",
        ]
    )

    email_address = Email(
        title=_(
            "title_organization_email_address",
            default="Email Address"
        ),
        required=False,
    )

    directives.widget("physical_address", AddressWidget)
    physical_address = AddressField(
        address_types="physical",
        subfield_validators={
            "country": "inline_field_validator",
            "state": "inline_field_validator",
            "district": "inline_field_validator",
        },
    ),

    directives.widget("postal_address", AddressWidget)
    postal_address = AddressField(
        address_types="postal",
        subfield_validators={
            "country": "inline_field_validator",
            "state": "inline_field_validator",
            "district": "inline_field_validator",
        },
    ),

    directives.widget("billing_address", AddressWidget)
    billing_address = AddressField(
        address_types="billing",
        subfield_validators={
            "country": "inline_field_validator",
            "state": "inline_field_validator",
            "district": "inline_field_validator",
        },
    ),

    model.fieldset(
        "bank_details",
        label=_(
            "title_bank_details_tab",
            default="Bank Details"
        ),
        fields=[
            "account_type",
            "account_name",
            "account_number",
            "bank_name",
            "bank_branch",
        ]
    )

    account_type = schema.TextLine(
        title=_(
            "title_organization_account_type",
            default="Account Type"
        ),
        required=False,
    )

    account_name = schema.TextLine(
        title=_(
            "title_organization_account_name",
            default="Account Name"
        ),
        required=False,
    )

    account_number = schema.TextLine(
        title=_(
            "title_organization_account_number",
            default="Account Number"
        ),
        required=False,
    )

    bank_name = schema.TextLine(
        title=_(
            "title_organization_account_bank_name",
            default="Bank Name"
        ),
        required=False,
    )

    bank_branch = schema.TextLine(
        title=_(
            "title_organization_account_bank_branch",
            default="Bank Branch"
        ),
        required=False,
    )


@implementer(IOrganizationSchema)
class Organization(Container):
    """Base class for Supplier content type
    """

    security = ClassSecurityInfo()

    def Title(self):
        """Return the name of the Organisation
        """
        name = self.getName()
        return safe_unicode(name).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setTitle(self, value):
        """Set the name of the Organisation
        """
        self.setName(value)

    @security.protected(permissions.View)
    def getName(self):
        accessor = self.accessor("name")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setName(self, value):
        mutator = self.mutator("name")
        mutator(self, value)

    @security.protected(permissions.View)
    def getTaxNumber(self):
        accessor = self.accessor("tax_number")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setTaxNumber(self, value):
        mutator = self.mutator("tax_number")
        mutator(self, value)

    @security.protected(permissions.View)
    def getPhone(self):
        accessor = self.accessor("phone")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setPhone(self, value):
        mutator = self.mutator("phone")
        mutator(self, value)

    @security.protected(permissions.View)
    def getFax(self):
        accessor = self.accessor("fax")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setFax(self, value):
        mutator = self.mutator("fax")
        mutator(self, value)

    @security.protected(permissions.View)
    def getEmailAddress(self):
        accessor = self.accessor("email_address")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEmailAddress(self, value):
        mutator = self.mutator("email_address")
        mutator(self, value)

    @security.protected(permissions.View)
    def getAccountType(self):
        accessor = self.accessor("account_type")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccountType(self, value):
        mutator = self.mutator("account_type")
        mutator(self, value)

    @security.protected(permissions.View)
    def getAccountName(self):
        accessor = self.accessor("account_name")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccountName(self, value):
        mutator = self.mutator("account_name")
        mutator(self, value)

    @security.protected(permissions.View)
    def getAccountNumber(self):
        accessor = self.accessor("account_number")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccountNumber(self, value):
        mutator = self.mutator("account_number")
        mutator(self, value)

    @security.protected(permissions.View)
    def getBankName(self):
        accessor = self.accessor("bank_name")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setBankName(self, value):
        mutator = self.mutator("bank_name")
        mutator(self, value)

    @security.protected(permissions.View)
    def getBankBranch(self):
        accessor = self.accessor("bank_branch")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setBankBranch(self, value):
        mutator = self.mutator("bank_branch")
        mutator(self, value)

    # def getPossibleAddresses(self):
    #     """Get the possible address fields
    #     """
    #     return ["PhysicalAddress", "PostalAddress", "BillingAddress"]
    #
    # def getPrintAddress(self):
    #     """Get an address for printing
    #     """
    #     address_lines = []
    #
    #     addresses = [
    #         self.getPostalAddress(),
    #         self.getPhysicalAddress(),
    #         self.getBillingAddress(),
    #     ]
    #
    #     for address in addresses:
    #         city = address.get("city", "")
    #         zip = address.get("zip", "")
    #         state = address.get("state", "")
    #         country = address.get("country", "")
    #
    #         if city:
    #             address_lines = [
    #                 address["address"].strip(),
    #                 "{} {}".format(city, zip).strip(),
    #                 "{} {}".format(state, country).strip(),
    #             ]
    #             break
    #
    #     return address_lines
