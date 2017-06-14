# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from decimal import Decimal

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.BaseFolder import BaseFolder
from Products.CMFCore.permissions import View
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFPlone.utils import safe_unicode
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.supplyorder import schema
from bika.lims.interfaces import ISupplyOrder
from persistent.mapping import PersistentMapping
from zope.component import getAdapter
from zope.interface import implements


class SupplyOrderLineItem(PersistentMapping):
    pass


class SupplyOrder(BaseFolder):
    implements(ISupplyOrder, IConstrainTypes)

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    supplyorder_lineitems = []

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getInvoiced(self):
        if self.getInvoice():
            return True
        else:
            return False

    def Title(self):
        """ Return the OrderNumber as title """
        return safe_unicode(self.getOrderNumber()).encode('utf-8')

    def getOrderNumber(self):
        return safe_unicode(self.getId()).encode('utf-8')

    def getContacts(self):
        adapter = getAdapter(self.aq_parent, name='getContacts')
        return adapter()

    security.declarePublic('getContactUIDForUser')

    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        r = self.portal_catalog(
            portal_type='Contact',
            getUsername=user_id
        )
        if len(r) == 1:
            return r[0].UID

    security.declareProtected(View, 'getTotalQty')

    def getTotalQty(self):
        """ Compute total qty """
        if self.supplyorder_lineitems:
            return sum(
                [obj['Quantity'] for obj in self.supplyorder_lineitems])
        return 0

    security.declareProtected(View, 'getSubtotal')

    def getSubtotal(self):
        """ Compute Subtotal """
        if self.supplyorder_lineitems:
            return sum(
                [(Decimal(obj['Quantity']) * Decimal(obj['Price'])) for obj in
                 self.supplyorder_lineitems])
        return 0

    security.declareProtected(View, 'getVATAmount')

    def getVATAmount(self):
        """ Compute VAT """
        return Decimal(self.getTotal()) - Decimal(self.getSubtotal())

    security.declareProtected(View, 'getTotal')

    def getTotal(self):
        """ Compute TotalPrice """
        total = 0
        for lineitem in self.supplyorder_lineitems:
            total += Decimal(lineitem['Quantity']) * \
                     Decimal(lineitem['Price']) * \
                     ((Decimal(lineitem['VAT']) / 100) + 1)
        return total

    def workflow_script_dispatch(self):
        """ dispatch order """
        self.setDateDispatched(DateTime())
        self.reindexObject()

    security.declareProtected(View, 'getProductUIDs')

    def getProductUIDs(self):
        """ return the uids of the products referenced by order items
        """
        uids = []
        for orderitem in self.objectValues('XupplyOrderItem'):
            product = orderitem.getProduct()
            if product is not None:
                uids.append(orderitem.getProduct().UID())
        return uids

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()


atapi.registerType(SupplyOrder, PROJECTNAME)
