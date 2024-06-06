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
from ComputedAttribute import ComputedAttribute
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from plone.supermodel import model
from plone.autoform import directives
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Item
from senaite.core.interfaces import IHavePrice
from senaite.core.interfaces import ILabProduct
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.interface import implementer
from zope.interface import provider
from zope.schema import Decimal
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def default_vat_factory(context):
    """Returns the default body text for publication emails
    """
    defaultVAT = api.get_setup().getVAT() or u"0.00"
    return Decimal().fromUnicode(defaultVAT)


class ILabProductSchema(model.Schema):
    """LabProduct Schema interface
    """

    title = schema.TextLine(
        title=_(
            "title_labproduct_title",
            default="Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            "title_labproduct_description",
            default="Description"
        ),
        required=False,
    )

    labproduct_volume = schema.TextLine(
        title=_(
            "title_labproduct_volume",
            default="Volume"
        ),
        required=False,
    )

    labproduct_unit = schema.TextLine(
        title=_(
            "title_labproduct_unit",
            default="Unit"
        ),
        required=False,
    )

    labproduct_price = schema.Decimal(
        title=_(
            "title_labproduct_price",
            default="Price (excluding VAT)"
        ),
        description=_(
            "description_labproduct_price",
            default="Please provide the price excluding VAT"
        ),
        required=False,
    )

    labproduct_vat = schema.Decimal(
        title=_(
            "title_labproduct_vat",
            default="VAT %"
        ),
        description=_(
            "description_labproduct_vat",
            default="Please provide the VAT in percent that is added to the "
                    "labproduct price"
        ),
        defaultFactory=default_vat_factory,
        required=False,
    )

    directives.mode(labproduct_vat_amount="display")
    directives.mode(IEditForm, labproduct_vat_amount="hidden")
    labproduct_vat_amount = schema.TextLine(
        title=_(
            "title_labproduct_vat_amount",
            default="VAT"
        ),
        readonly=True)

    directives.mode(labproduct_total_price="display")
    directives.mode(IEditForm, labproduct_total_price="hidden")
    labproduct_total_price = schema.TextLine(
        title=_(
            "title_labproduct_total_price",
            default="Total Price"
        ),
        readonly=True)


@implementer(ILabProduct, ILabProductSchema, IHavePrice, IDeactivable)
class LabProduct(Item):
    """LabProduct content
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getVolume(self):
        accessor = self.accessor("labproduct_volume")
        value = accessor(self) or ""
        return api.to_utf8(value)

    @security.protected(permissions.ModifyPortalContent)
    def setVolume(self, value):
        mutator = self.mutator("labproduct_volume")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    Volume = property(getVolume, setVolume)

    @security.protected(permissions.View)
    def getUnit(self):
        accessor = self.accessor("labproduct_unit")
        value = accessor(self) or ""
        return api.to_utf8(value)

    @security.protected(permissions.ModifyPortalContent)
    def setUnit(self, value):
        mutator = self.mutator("labproduct_unit")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    Unit = property(getUnit, setUnit)

    @security.protected(permissions.View)
    def getPrice(self):
        accessor = self.accessor("labproduct_price")
        value = accessor(self) or ""
        return api.to_utf8(value)

    @security.protected(permissions.ModifyPortalContent)
    def setPrice(self, value):
        mutator = self.mutator("labproduct_price")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    Price = property(getPrice, setPrice)

    @security.protected(permissions.View)
    def getVAT(self):
        accessor = self.accessor("labproduct_vat")
        value = accessor(self) or ""
        return api.to_utf8(str(value))

    @security.protected(permissions.ModifyPortalContent)
    def setVAT(self, value):
        mutator = self.mutator("labproduct_vat")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    VAT = property(getVAT, setVAT)

    def getDefaultVAT(self):
        """ return default VAT from setup """
        return api.get_setup().getVAT() or "0.00"

    @security.protected(permissions.View)
    def getVATAmount(self):
        """ Compute VATAmount
        """
        try:
            vatamount = self.getTotalPrice() - Decimal(self.getPrice())
        except Exception:
            vatamount = Decimal('0.00')
        return vatamount.quantize(Decimal('0.00'))

    labproduct_vat_amount = ComputedAttribute(getVATAmount, 1)

    # BBB: AT schema (computed) field property
    VATAmount = property(getVATAmount)

    def getTotalPrice(self):
        """ compute total price """
        price = Decimal().fromUnicode(self.getPrice() or u"0.00")
        vat = Decimal().fromUnicode(self.getVAT() or u"0.00")
        vat = vat and vat / 100 or 0
        price = price + (price * vat)
        return price.quantize(Decimal().fromUnicode(u"0.00"))

    labproduct_total_price = ComputedAttribute(getTotalPrice, 1)

    # BBB: AT schema (computed) field property
    TotalPrice = property(getTotalPrice)
