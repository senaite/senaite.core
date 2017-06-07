# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from decimal import Decimal

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema

Volume = StringField(
    'Volume',
    widget=StringWidget(
        label=_("Volume")
    )
)

Unit = StringField(
    'Unit',
    widget=StringWidget(
        label=_("Unit")
    )
)

VAT = FixedPointField(
    'VAT',
    default_method='getDefaultVAT',
    widget=DecimalWidget(
        label=_("VAT %"),
        description=_("Enter percentage value eg. 14.0")
    )
)

Price = FixedPointField(
    'Price',
    required=1,
    widget=DecimalWidget(
        label=_("Price excluding VAT")
    )
)

VATAmount = ComputedField(
    'VATAmount',
    expression='context.getVATAmount()',
    widget=ComputedWidget(
        label=_("VAT"),
        visible={'edit': 'hidden', }
    )
)

TotalPrice = ComputedField(
    'TotalPrice',
    expression='context.getTotalPrice()',
    widget=ComputedWidget(
        label=_("Total price"),
        visible={'edit': 'hidden'}
    )
)

schema = BikaSchema.copy() + Schema((
    Volume,
    Unit,
    VAT,
    Price,
    VATAmount,
    TotalPrice
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True


class LabProduct(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getTotalPrice(self):
        """ compute total price """
        price = self.getPrice()
        price = Decimal(price or '0.00')
        vat = Decimal(self.getVAT())
        vat = vat and vat / 100 or 0
        price = price + (price * vat)
        return price.quantize(Decimal('0.00'))

    def getDefaultVAT(self):
        """ return default VAT from bika_setup """
        try:
            vat = self.bika_setup.getVAT()
            return vat
        except (ValueError, TypeError):
            return "0.00"

    security.declarePublic('getVATAmount')

    def getVATAmount(self):
        """ Compute VATAmount
        """
        try:
            vatamount = self.getTotalPrice() - Decimal(self.getPrice())
        except (ValueError, TypeError):
            vatamount = Decimal('0.00')
        return vatamount.quantize(Decimal('0.00'))


registerType(LabProduct, PROJECTNAME)
