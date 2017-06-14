# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseFolder import BaseFolder
from persistent.mapping import PersistentMapping
from decimal import Decimal

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.CMFCore.permissions import View
from Products.CMFPlone.utils import safe_unicode
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.invoice import schema
from bika.lims.interfaces import IInvoice
from zope.interface import implements


class Invoice(BaseFolder):
    implements(IInvoice)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Invoice Id as title """
        return safe_unicode(self.getId()).encode('utf-8')

    security.declareProtected(View, 'getSubtotal')

    def getSubtotal(self):
        """ Compute Subtotal """
        return sum([float(obj['Subtotal']) for obj in self.invoice_lineitems])

    security.declareProtected(View, 'getVATAmount')

    def getVATAmount(self):
        """ Compute VAT """
        return Decimal(self.getTotal()) - Decimal(self.getSubtotal())

    security.declareProtected(View, 'getTotal')

    def getTotal(self):
        """ Compute Total """
        return sum([float(obj['Total']) for obj in self.invoice_lineitems])

    security.declareProtected(View, 'getInvoiceSearchableText')

    def getInvoiceSearchableText(self):
        """ Aggregate text of all line items for querying """
        s = ''
        for item in self.invoice_lineitems:
            s = s + item['ItemDescription']
        return s

    def workflow_script_dispatch(self):
        """ dispatch order """
        self.setDateDispatched(DateTime())

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()


registerType(Invoice, PROJECTNAME)


class InvoiceLineItem(PersistentMapping):
    pass
