# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.config import ManageInvoices
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.invoice import InvoiceLineItem
from bika.lims.interfaces import ICancellable
from bika.lims.interfaces import IInvoiceBatch
from bika.lims.utils import get_invoice_item_description
from bika.lims.workflow import getTransitionDate
from DateTime import DateTime
from Products.Archetypes.public import DateTimeField
from Products.Archetypes.public import CalendarWidget
from Products.Archetypes.public import registerType
from Products.Archetypes.public import Schema
from Products.Archetypes.public import BaseFolder
from Products.CMFPlone.utils import _createObjectByType
from zope.container.contained import ContainerModifiedEvent
from zope.interface import implements


schema = BikaSchema.copy() + Schema((
    DateTimeField(
        "BatchStartDate",
        required=1,
        default_method="current_date",
        widget=CalendarWidget(
            label=_("Start Date"),
        ),
    ),
    DateTimeField(
        "BatchEndDate",
        required=1,
        default_method="current_date",
        validators=("invoicebatch_EndDate_validator",),
        widget=CalendarWidget(
            label=_("End Date"),
        ),
    ),
))

schema["title"].default = DateTime().strftime("%b %Y")


class InvoiceBatch(BaseFolder):
    """Container for Invoice instances
    """
    implements(IInvoiceBatch, ICancellable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    @security.protected(ManageInvoices)
    def invoices(self):
        return self.objectValues("Invoice")

    @security.protected(ManageInvoices)
    def createInvoice(self, client_uid, items):
        """Creates and invoice for a client and a set of items
        """
        plone_view = self.restrictedTraverse('@@plone')
        invoice_id = self.generateUniqueId('Invoice')
        invoice = _createObjectByType("Invoice", self, invoice_id)
        # noinspection PyCallingNonCallable
        invoice.edit(
            Client=client_uid,
            InvoiceDate=DateTime(),
        )

        invoice.processForm()
        invoice.invoice_lineitems = []
        for item in items:
            lineitem = InvoiceLineItem()
            if item.portal_type == 'AnalysisRequest':
                lineitem['ItemDate'] = plone_view.toLocalizedTime(
                    getTransitionDate(item, 'publish'), long_format=1)
                lineitem['OrderNumber'] = item.getId()
                lineitem['AnalysisRequest'] = item
                lineitem['SupplyOrder'] = ''
                description = get_invoice_item_description(item)
                lineitem['ItemDescription'] = description
            elif item.portal_type == 'SupplyOrder':
                lineitem['ItemDate'] = item.getDateDispatched()
                lineitem['OrderNumber'] = item.getOrderNumber()
                lineitem['AnalysisRequest'] = ''
                lineitem['SupplyOrder'] = item
                description = get_invoice_item_description(item)
                lineitem['ItemDescription'] = description
            lineitem['Subtotal'] = item.getSubtotal()
            lineitem['VATAmount'] = item.getVATAmount()
            lineitem['Total'] = item.getTotal()
            invoice.invoice_lineitems.append(lineitem)
        invoice.reindexObject()
        return invoice

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        # noinspection PyCallingNonCallable
        return DateTime()


registerType(InvoiceBatch, PROJECTNAME)


def ObjectModifiedEventHandler(instance, event):
    """ Various types need automation on edit.
    """
    # if not hasattr(instance, 'portal_type'):
    #     return

    # if instance.portal_type == 'InvoiceBatch':

    if not isinstance(event, ContainerModifiedEvent):
        """ Create batch invoices
        """
        start = instance.getBatchStartDate()
        end = instance.getBatchEndDate()
        # Query for ARs in date range
        query = {
            'portal_type': 'AnalysisRequest',
            'review_state': 'published',
            'getInvoiceExclude': False,
            'getDatePublished': {
                'range': 'min:max',
                'query': [start, end]
            }
        }
        ars = instance.bika_catalog(query)
        # Query for Orders in date range
        query = {
            'portal_type': 'SupplyOrder',
            'review_state': 'dispatched',
            'getDateDispatched': {
                'range': 'min:max',
                'query': [start, end]
            }
        }
        orders = instance.portal_catalog(query)
        # Make list of clients from found ARs and Orders
        clients = {}
        for rs in (ars, orders):
            for p in rs:
                obj = p.getObject()
                if obj.getInvoiced():
                    continue
                client_uid = obj.aq_parent.UID()
                l = clients.get(client_uid, [])
                l.append(obj)
                clients[client_uid] = l
        # Create an invoice for each client
        for client_uid, items in clients.items():
            instance.createInvoice(client_uid, items)
