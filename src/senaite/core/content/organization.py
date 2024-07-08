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
from senaite.core.schema.addressfield import BILLING_ADDRESS
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.schema.addressfield import POSTAL_ADDRESS
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

    title = schema.TextLine(
        title=_(
            u"title_organization_name",
            default=u"Name"
        ),
        required=True,
    )

    tax_number = schema.TextLine(
        title=_(
            u"title_organization_tax_number",
            default=u"VAT number"
        ),
        required=False,
    )

    phone = schema.TextLine(
        title=_(
            u"title_organization_phone",
            default=u"Phone"
        ),
        required=False,
    )

    fax = schema.TextLine(
        title=_(
            u"title_organization_fax",
            default=u"Fax"
        ),
        required=False,
    )

    model.fieldset(
        "addresses",
        label=_(
            u"title_addresses_tab",
            default=u"Address"
        ),
        fields=[
            "email",
            "address_list",
        ]
    )

    email = Email(
        title=_(
            u"title_organization_email",
            default=u"Email"
        ),
        required=False,
    )

    directives.widget("address_list", AddressWidget)
    address_list = AddressField(
        address_types=(
            PHYSICAL_ADDRESS, POSTAL_ADDRESS, BILLING_ADDRESS,
        ),
        required=False,
    )

    model.fieldset(
        "bank_details",
        label=_(
            u"title_bank_details_tab",
            default=u"Bank Details"
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
            u"title_organization_account_type",
            default=u"Account Type"
        ),
        required=False,
    )

    account_name = schema.TextLine(
        title=_(
            u"title_organization_account_name",
            default=u"Account Name"
        ),
        required=False,
    )

    account_number = schema.TextLine(
        title=_(
            u"title_organization_account_number",
            default=u"Account Number"
        ),
        required=False,
    )

    bank_name = schema.TextLine(
        title=_(
            u"title_organization_account_bank_name",
            default=u"Bank Name"
        ),
        required=False,
    )

    bank_branch = schema.TextLine(
        title=_(
            u"title_organization_account_bank_branch",
            default=u"Bank Branch"
        ),
        required=False,
    )


@implementer(IOrganizationSchema)
class Organization(Container):
    """Base class for Supplier content type
    """

    security = ClassSecurityInfo()

    # for backward compatibility: title -> name
    @security.protected(permissions.View)
    def getName(self):
        accessor = self.accessor("title")
        return accessor(self).encode("utf-8")

    # for backward compatibility: name -> title
    @security.protected(permissions.ModifyPortalContent)
    def setName(self, value):
        mutator = self.mutator("title")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    Name = property(getName, setName)

    @security.protected(permissions.View)
    def getTaxNumber(self):
        accessor = self.accessor("tax_number")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setTaxNumber(self, value):
        mutator = self.mutator("tax_number")
        mutator(self, value)

    # BBB: AT schema field property
    TaxNumber = property(getTaxNumber, setTaxNumber)

    @security.protected(permissions.View)
    def getPhone(self):
        accessor = self.accessor("phone")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setPhone(self, value):
        mutator = self.mutator("phone")
        mutator(self, value)

    # BBB: AT schema field property
    Phone = property(getPhone, setPhone)

    @security.protected(permissions.View)
    def getFax(self):
        accessor = self.accessor("fax")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setFax(self, value):
        mutator = self.mutator("fax")
        mutator(self, value)

    # BBB: AT schema field property
    Fax = property(getFax, setFax)

    @security.protected(permissions.View)
    def getEmail(self):
        accessor = self.accessor("email")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setEmail(self, value):
        mutator = self.mutator("email")
        mutator(self, value)

    # for backward compatibility
    @security.protected(permissions.View)
    def getEmailAddress(self):
        return self.getEmail()

    # for backward compatibility
    @security.protected(permissions.ModifyPortalContent)
    def setEmailAddress(self, value):
        self.setEmail(value)

    # BBB: AT schema field property
    EmailAddress = property(getEmailAddress, setEmailAddress)

    @security.protected(permissions.View)
    def getAccountType(self):
        accessor = self.accessor("account_type")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccountType(self, value):
        mutator = self.mutator("account_type")
        mutator(self, value)

    # BBB: AT schema field property
    AccountType = property(getAccountType, setAccountType)

    @security.protected(permissions.View)
    def getAccountName(self):
        accessor = self.accessor("account_name")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setAccountName(self, value):
        mutator = self.mutator("account_name")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    AccountName = property(getAccountName, setAccountName)

    @security.protected(permissions.View)
    def getAccountNumber(self):
        accessor = self.accessor("account_number")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccountNumber(self, value):
        mutator = self.mutator("account_number")
        mutator(self, value)

    # BBB: AT schema field property
    AccountNumber = property(getAccountNumber, setAccountNumber)

    @security.protected(permissions.View)
    def getBankName(self):
        accessor = self.accessor("bank_name")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setBankName(self, value):
        mutator = self.mutator("bank_name")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    BankName = property(getBankName, setBankName)

    @security.protected(permissions.View)
    def getBankBranch(self):
        accessor = self.accessor("bank_branch")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setBankBranch(self, value):
        mutator = self.mutator("bank_branch")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    BankBranch = property(getBankBranch, setBankBranch)

    @security.protected(permissions.View)
    def getAddressList(self):
        accessor = self.accessor("address_list")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAddressList(self, value):
        mutator = self.mutator("address_list")
        mutator(self, value)

    def getPhysicalAddress(self):
        return self._get_address_by_type(PHYSICAL_ADDRESS)

    def getPostalAddress(self):
        return self._get_address_by_type(POSTAL_ADDRESS)

    def getBillingAddress(self):
        return self._get_address_by_type(BILLING_ADDRESS)

    def _get_address_by_type(self, address_type):
        accessor = self.accessor("address_list")
        address_list = accessor(self)
        result = list(filter(lambda item: item.get("type") == address_type,
                             address_list))

        return result[0] if len(result) else {}

    def _format_address_line(self, address):
        city = address.get("city", "")
        zip = address.get("zip", "")
        country = address.get("country", "")

        address_lines = [
            address["address"].strip(),
            "{} {}".format(city, zip).strip(),
            "{}".format(country).strip(),
        ]

        return address_lines

    def getPrintAddress(self):
        """Get an address for printing
        """
        address_lines = []
        addresses = [
            self._get_address_by_type(POSTAL_ADDRESS),
            self._get_address_by_type(PHYSICAL_ADDRESS),
            self._get_address_by_type(BILLING_ADDRESS),
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
