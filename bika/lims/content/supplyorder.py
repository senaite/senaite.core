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

import sys
from decimal import Decimal

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import ComputedField
from Products.Archetypes.public import ComputedWidget
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import TextField
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFPlone.utils import safe_unicode
from persistent.mapping import PersistentMapping
from zope.component import getAdapter
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.browser.widgets import ReferenceWidget as BikaReferenceWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import ICancellable
from bika.lims.interfaces import ISupplyOrder

schema = BikaSchema.copy() + Schema((
    ReferenceField(
      'Contact',
      required=1,
      vocabulary_display_path_bound=sys.maxsize,
      allowed_types=('Contact',),
      referenceClass=HoldingReference,
      relationship='SupplyOrderContact',
      widget=BikaReferenceWidget(
        render_own_label=True,
        showOn=True,
        colModel=[
          {'columnName': 'UID', 'hidden': True},
          {'columnName': 'Fullname', 'width': '50', 'label': _('Name')},
          {'columnName': 'EmailAddress', 'width': '50', 'label': _('Email Address')},
        ],
      ),
    ),
    StringField('OrderNumber',
                required=1,
                searchable=True,
                widget=StringWidget(
                    label=_("Order Number"),
                    ),
                ),
    ReferenceField('Invoice',
                   vocabulary_display_path_bound=sys.maxsize,
                   allowed_types=('Invoice',),
                   referenceClass=HoldingReference,
                   relationship='OrderInvoice',
                   ),
    DateTimeField(
      'OrderDate',
      required=1,
      default_method='current_date',
      widget=DateTimeWidget(
        label=_("Order Date"),
        size=12,
        render_own_label=True,
        visible={
          'edit': 'visible',
          'view': 'visible',
          'add': 'visible',
          'secondary': 'invisible'
        },
      ),
    ),
    DateTimeField('DateDispatched',
                  widget=DateTimeWidget(
                      label=_("Date Dispatched"),
                      ),
                  ),
    TextField(
        "Remarks",
        allowable_content_types=("text/plain",),
        widget=TextAreaWidget(
            label=_("Remarks"),
        )
    ),
    ComputedField('ClientUID',
                  expression = 'here.aq_parent.UID()',
                  widget = ComputedWidget(
                      visible=False,
                      ),
                  ),
    ComputedField('ProductUID',
                  expression = 'context.getProductUIDs()',
                  widget = ComputedWidget(
                      visible=False,
                      ),
                  ),
),
)

schema['title'].required = False

class SupplyOrderLineItem(PersistentMapping):
    pass

class SupplyOrder(BaseFolder):

    implements(ISupplyOrder, IConstrainTypes, ICancellable)

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
                [(Decimal(obj['Quantity']) * Decimal(obj['Price'])) for obj in self.supplyorder_lineitems])
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
                     Decimal(lineitem['Price']) *  \
                     ((Decimal(lineitem['VAT']) /100) + 1)
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
