# -*- coding: utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.utils import DisplayList, IntDisplayList
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.content.schema.abstractanalysis import schema
from bika.lims.utils import to_utf8 as _c


class AbstractBaseAnalysis(BaseContent):  # TODO BaseContent?  is really needed?
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    @security.public
    def _getCatalogTool(self):
        from bika.lims.catalog import getCatalog
        return getCatalog(self)

    @security.public
    def Title(self):
        return _c(self.title)

    @security.public
    def getDefaultVAT(self):
        """Return default VAT from bika_setup
        """
        try:
            vat = self.bika_setup.getVAT()
            return vat
        except ValueError:
            return "0.00"

    @security.public
    def getVATAmount(self):
        """Compute VAT Amount from the Price and system configured VAT
        """
        price, vat = self.getPrice(), self.getVAT()
        return float(price) * (float(vat) / 100)

    @security.public
    def getDiscountedPrice(self):
        """Compute discounted price excl. VAT
        """
        price = self.getPrice()
        price = price and price or 0
        discount = self.bika_setup.getMemberDiscount()
        discount = discount and discount or 0
        return float(price) - (float(price) * float(discount)) / 100

    @security.public
    def getDiscountedBulkPrice(self):
        """Compute discounted bulk discount excl. VAT
        """
        price = self.getBulkPrice()
        price = price and price or 0
        discount = self.bika_setup.getMemberDiscount()
        discount = discount and discount or 0
        return float(price) - (float(price) * float(discount)) / 100

    @security.public
    def getTotalPrice(self):
        """Compute total price including VAT
        """
        price = self.getPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    @security.public
    def getTotalBulkPrice(self):
        """Compute total bulk price
        """
        price = self.getBulkPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    @security.public
    def getTotalDiscountedPrice(self):
        """Compute total discounted price
        """
        price = self.getDiscountedPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    @security.public
    def getTotalDiscountedBulkPrice(self):
        """Compute total discounted corporate bulk price
        """
        price = self.getDiscountedCorporatePrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat or 0
        return float(price) + (float(price) * float(vat)) / 100

    @security.public
    def getAnalysisCategories(self):
        """A vocabulary listing available (and activated) categories.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        cats = bsc(portal_type='AnalysisCategory', inactive_state='active')
        items = [(o.UID, o.Title) for o in cats]
        o = self.getCategory()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    @security.public
    def getDepartments(self):
        """A vocabulary listing available (and activated) departments.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(o.UID, o.Title) for o in
                              bsc(portal_type='Department',
                                  inactive_state='active')]
        o = self.getDepartment()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))

    @security.public
    def getLowerDetectionLimit(self):
        """Returns the Lower Detection Limit for this service as a floatable
        """
        ldl = self.getField('LowerDetectionLimit').get(self)
        try:
            return float(ldl)
        except ValueError:
            return 0

    @security.public
    def getUpperDetectionLimit(self):
        """Returns the Upper Detection Limit for this service as a floatable
        """
        udl = self.getField('UpperDetectionLimit').get(self)
        try:
            return float(udl)
        except ValueError:
            return 0

    @security.public
    def isSelfVerificationEnabled(self):
        """Returns if the user that submitted a result for this analysis must
        also be able to verify the result
        :returns: true or false
        """
        bsve = self.bika_setup.getSelfVerificationEnabled()
        vs = self.getSelfVerification()
        return bsve if vs == -1 else vs == 1

    @security.public
    def _getSelfVerificationVocabulary(self):
        """Returns a DisplayList with the available options for the
        self-verification list: 'system default', 'true', 'false'
        :returns: DisplayList with the available options for the
        self-verification list
        """
        bsve = self.bika_setup.getSelfVerificationEnabled()
        bsve = _('Yes') if bsve else _('No')
        bsval = "%s (%s)" % (_("System default"), bsve)
        items = [(-1, bsval), (0, _('No')), (1, _('Yes'))]
        return IntDisplayList(list(items))

    @security.public
    def getNumberOfRequiredVerifications(self):
        """Returns the number of required verifications a test for this
        analysis requires before being transitioned to 'verified' state
        :returns: number of required verifications
        """
        num = self.getField('NumberOfRequiredVerifications').get(self)
        if num < 1:
            return self.bika_setup.getNumberOfRequiredVerifications()
        return num

    @security.public
    def _getNumberOfRequiredVerificationsVocabulary(self):
        """Returns a DisplayList with the available options for the
        multi-verification list: 'system default', '1', '2', '3', '4'
        :returns: DisplayList with the available options for the
        multi-verification list
        """
        bsve = self.bika_setup.getNumberOfRequiredVerifications()
        bsval = "%s (%s)" % (_("System default"), str(bsve))
        items = [(-1, bsval), (1, '1'), (2, '2'), (3, '3'), (4, '4')]
        return IntDisplayList(list(items))

    @security.public
    def getMethodTitle(self):
        """This is used to populate catalog values
        """
        method = self.getMethod()
        if method:
            return method.Title()

    @security.public
    def getMethodUID(self):
        """This is used to populate catalog values
        """
        method = self.getMethod()
        if method:
            return method.UID()

    @security.public
    def getMethodURL(self):
        """This is used to populate catalog values
        """
        method = self.getMethod()
        if method:
            return method.absolute_url_path()

    @security.public
    def getInstrumentTitle(self):
        """Used to populate catalog values
        """
        instrument = self.getInstrument()
        if instrument:
            return instrument.Title()

    @security.public
    def getInstrumentUID(self):
        """Used to populate catalog values
        """
        instrument = self.getInstrument()
        if instrument:
            return instrument.UID()

    @security.public
    def getInstrumentURL(self):
        """Used to populate catalog values
        """
        instrument = self.getInstrument()
        if instrument:
            return instrument.absolute_url_path()

    @security.public
    def getCalculationTitle(self):
        """Used to populate catalog values
        """
        calculation = self.getCalculation()
        if calculation:
            return calculation.Title()

    @security.public
    def getCalculationUID(self):
        """Used to populate catalog values
        """
        calculation = self.getCalculation()
        if calculation:
            return calculation.UID()

    @security.public
    def getCategoryTitle(self):
        """Used to populate catalog values
        """
        category = self.getCategory()
        if category:
            return category.Title()

    @security.public
    def getCategoryUID(self):
        """Used to populate catalog values
        """
        category = self.getCategory()
        if category:
            return category.UID()

    @security.public
    def getDepartmentTitle(self):
        """Used to populate catalog values
        """
        department = self.getDepartment()
        if department:
            return department.Title()

    @security.public
    def getDepartmentUID(self):
        """Used to populate catalog values
        """
        department = self.getDepartment()
        if department:
            return department.UID()
