# -*- coding: utf-8 -*-
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from decimal import Decimal

from AccessControl import ClassSecurityInfo
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.labproduct import schema


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
