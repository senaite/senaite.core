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
from bika.lims.interfaces import IDeactivable
from bika.lims.validators import country_dic
from bika.lims.validators import letter_dic
from bika.lims.validators import _toIntList
from bika.lims.validators import _sumLists
from senaite.core.i18n import translate
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.content.organization import IOrganizationSchema
from senaite.core.content.organization import Organization
from senaite.core.interfaces import ISupplier
from plone.supermodel import model
from Products.CMFCore import permissions
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


class ISupplierSchema(IOrganizationSchema):
    """Schema interface
    """

    remarks = schema.Text(
        title=_(
            "title_supplier_remarks",
            default="Remarks",
        ),
        required=False,
    )

    website = schema.TextLine(
        title=_(
            "title_supplier_website",
            default="Website",
        ),
        required=False,
    )

    model.fieldset(
        "bank_details",
        label=_(
            "Accounting",
            default="Bank Details"
        ),
        fields=[
            "nib",
            "ibn",
            "swift_code",
        ]
    )

    nib = schema.TextLine(
        title=_(
            "title_supplier_nib",
            default="NIB",
        ),
        required=False,
    )

    ibn = schema.TextLine(
        title=_(
            "title_supplier_ibn",
            default="IBN",
        ),
        required=False,
    )

    swift_code = schema.TextLine(
        title=_(
            "title_supplier_swift_code",
            default="SWIFT code",
        ),
        required=False,
    )

    lab_account_number = schema.TextLine(
        title=_(
            "title_supplier_lab_contact_number",
            default="Lab Account Number",
        ),
        required=False,
    )

    @invariant
    def validate_nib(data):
        """Checks NIB field for float value if exist
        """
        src_nib = getattr(data, "nib", None)
        if src_nib is None:
            return

        LEN_NIB = 21
        table = (73, 17, 89, 38, 62, 45, 53, 15, 50, 5, 49, 34, 81, 76, 27, 90,
                 9, 30, 3)

        # convert to entire numbers list
        nib = _toIntList(src_nib)

        # checking the length of the number
        if len(nib) != LEN_NIB:
            msg = translate(_('Incorrect NIB number: %s' % src_nib))
            raise Invalid(msg)

        # last numbers algorithm validator
        left_part = nib[-2] * 10 + nib[-1]
        right_part = 98 - _sumLists(table, nib[:-2]) % 97
        if left_part != right_part:
            raise Invalid("Invalid NIB number")

    @invariant
    def validate_ibn(data):
        """Checks IBN field for float value if exist
        """
        ibn = getattr(data, "ibn", None)
        if ibn is None:
            return

        # remove spaces from formatted
        IBAN = ''.join(c for c in ibn if c.isalnum())

        IBAN = IBAN[4:] + IBAN[:4]
        country = IBAN[-4:-2]

        if country not in country_dic:
            msg = translate(_('Unknown IBAN country %s' % country))
            raise Invalid(msg)

        length_c, name_c = country_dic[country]

        if len(IBAN) != length_c:
            diff = len(IBAN) - length_c
            warn_len = ('short by %i' % -diff) if diff < 0 \
                else ('too long by %i' % diff)
            msg = translate(_('Wrong IBAN length by %s: %s' % (warn_len, ibn)))
            raise Invalid(msg)
        # Validating procedure
        elif int("".join(str(letter_dic[x]) for x in IBAN)) % 97 != 1:
            msg = translate(_('Incorrect IBAN number: %s' % ibn))
            raise Invalid(msg)


@implementer(ISupplier, ISupplierSchema, IDeactivable)
class Supplier(Organization):
    """A container for Supplier
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getRemarks(self):
        accessor = self.accessor("remarks")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setRemarks(self, value):
        mutator = self.mutator("remarks")
        mutator(self, value)

    # BBB: AT schema field property
    Remarks = property(getRemarks, setRemarks)

    @security.protected(permissions.View)
    def getWebsite(self):
        accessor = self.accessor("website")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setWebsite(self, value):
        mutator = self.mutator("website")
        mutator(self, value)

    # BBB: AT schema field property
    Website = property(getWebsite, setWebsite)

    @security.protected(permissions.View)
    def getNib(self):
        accessor = self.accessor("nib")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setNib(self, value):
        mutator = self.mutator("nib")
        mutator(self, value)

    # BBB: AT schema field property
    NIB = property(getNib, setNib)

    @security.protected(permissions.View)
    def getIbn(self):
        accessor = self.accessor("ibn")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setIbn(self, value):
        mutator = self.mutator("ibn")
        mutator(self, value)

    # BBB: AT schema field property
    IBN = property(getIbn, setIbn)

    @security.protected(permissions.View)
    def getSwiftCode(self):
        accessor = self.accessor("swift_code")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSwiftCode(self, value):
        mutator = self.mutator("swift_code")
        mutator(self, value)

    # BBB: AT schema field property
    SWIFTcode = property(getSwiftCode, setSwiftCode)

    @security.protected(permissions.View)
    def getLabAccountNumber(self):
        accessor = self.accessor("lab_account_number")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setLabAccountNumber(self, value):
        mutator = self.mutator("lab_account_number")
        mutator(self, value)

    # BBB: AT schema field property
    LabAccountNumber = property(getLabAccountNumber, setLabAccountNumber)
