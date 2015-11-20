"""InvoiceBatch is a container for Invoice instances.
"""
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.utils import _createObjectByType
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import ManageInvoices, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.invoice import InvoiceLineItem
from bika.lims.interfaces import IInvoiceBatch
from bika.lims.utils import get_invoice_item_description
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from bika.lims.workflow import isBasicTransitionAllowed
from zope.container.contained import ContainerModifiedEvent
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    DateTimeField('BatchStartDate',
        required=1,
        default_method='current_date',
        widget=CalendarWidget(
            label=_("Start Date"),
        ),
    ),
    DateTimeField('BatchEndDate',
        required=1,
        default_method='current_date',
        widget=CalendarWidget(
            label=_("End Date"),
        ),
    ),
),
)

schema['title'].default = DateTime().strftime('%b %Y')


class InvoiceBatch(BaseFolder):

    """ Container for Invoice instances """
    implements(IInvoiceBatch)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declareProtected(ManageInvoices, 'invoices')

    def invoices(self):
        return self.objectValues('Invoice')

    # security.declareProtected(PostInvoiceBatch, 'post')
    # def post(self, REQUEST = None):
    #     """ Post invoices
    #     """
    #     map (lambda e: e._post(), self.invoices())
    #     if REQUEST:
    #         REQUEST.RESPONSE.redirect('invoicebatch_invoices')

    security.declareProtected(ManageInvoices, 'createInvoice')

    def createInvoice(self, client_uid, items):
        """ Creates and invoice for a client and a set of items
        """
        invoice_id = self.generateUniqueId('Invoice')
        invoice = _createObjectByType("Invoice", self, invoice_id)
        invoice.edit(
            Client=client_uid,
            InvoiceDate=DateTime(),
        )
        invoice.processForm()
        invoice.invoice_lineitems = []
        for item in items:
            lineitem = InvoiceLineItem()
            if item.portal_type == 'AnalysisRequest':
                lineitem['ItemDate'] = item.getDatePublished()
                lineitem['OrderNumber'] = item.getRequestID()
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
        return DateTime()

    def guard_cancel_transition(self):
        if not isBasicTransitionAllowed(self):
            return False
        return True

    def guard_reinstate_transition(self):
        if not isBasicTransitionAllowed(self):
            return False
        return True

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
