"""InvoiceBatch is a container for Invoice instances.
"""
from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.config import ManageInvoices, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.invoice import InvoiceLineItem
from bika.lims.interfaces import IInvoiceBatch
from bika.lims.utils import get_invoice_item_description
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.CMFCore import permissions
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

    # security.declareProtected(ManageInvoices, 'invoicebatch_export')
    # def invoicebatch_export(self, REQUEST, RESPONSE):
    #     """ Export invoice batch in csv format.
    #     Writes the csv file into the RESPONSE to allow
    #     the file to be streamed to the user.
    #     Nothing gets returned.
    #     """
    #     import csv
    #     from cStringIO import StringIO
    #     delimiter = ','
    #     filename = 'batch.txt'

    #     container = self.unrestrictedTraverse(REQUEST.get('current_path'))
    #     assert(container)

    #     container.plone_log("Exporting InvoiceBatch to CSV format for PASTEL")
    #     invoices = container.listFolderContents()

    #     if (not len(invoices)):
    #         container.plone_log("InvoiceBatch contains no entries")

    #     rows = []
    #     _ordNum = 'starting at none'
    #     for invoice in invoices:
    #         new_invoice = True
    #         _invNum = "%s" % invoice.getId()[:8]
    #         _clientNum = "%s" % invoice.getClient().getAccountNumber()
    #         _invDate = "%s" % invoice.getInvoiceDate().strftime('%Y-%m-%d')
    #         _monthNum = invoice.getInvoiceDate().month()
    #         if _monthNum < 7:
    #             _periodNum = _monthNum + 6
    #         else:
    #             _periodNum = _monthNum - 6
    #         _periodNum = "%s" % _monthNum

    #         _message1 = ''
    #         _message2 = ''
    #         _message3 = ''

    # items = invoice.invoice_lineitems # objectValues('InvoiceLineItem')
    #         mixed = [(item.getClientOrderNumber(), item) for item in items]
    #         mixed.sort()
    #         lines = [t[1] for t in mixed]

    # iterate through each invoice line
    #         for line in lines:
    #             if new_invoice or line.getClientOrderNumber() != _ordNum:
    #                 new_invoice = False
    #                 _ordNum = line.getClientOrderNumber()

    # create header csv entry as a list
    #                 header = [ \
    #                     "Header", _invNum, " ", " ", _clientNum, _periodNum, \
    #                     _invDate, _ordNum, "N", 0, _message1, _message2, \
    #                     _message3, "", "", "", "", "", "", 0, "", "", "", "", \
    #                     0, "", "", "N"]
    #                 rows.append(header)

    #             _quant = 1
    #             _unitp = line.getSubtotal()
    #             _inclp = line.getTotal()
    #             _item = line.getItemDescription()
    #             _desc = "Analysis: %s" % _item[:40]
    #             if _item.startswith('Water') or _item.startswith('water'):
    #                 _icode = "002"
    #             else:
    #                 _icode = "001"
    #             _ltype = "4"
    #             _ccode = ""
    # create detail csv entry as a list
    #             detail = ["Detail", 0, _quant, _unitp, _inclp, \
    #                       "", "01", "0", "0", _icode, _desc, \
    #                       _ltype, _ccode, ""]
    #             rows.append(detail)
    # convert lists to csv string
    #     ramdisk = StringIO()
    #     writer = csv.writer(ramdisk, delimiter = delimiter)
    #     assert(writer)
    #     writer.writerows(rows)
    #     result = ramdisk.getvalue()
    #     ramdisk.close()
    # stream file to browser
    #     setheader = RESPONSE.setHeader
    #     setheader('Content-Length', len(result))
    #     setheader('Content-Type',
    #         'text/x-comma-separated-values')
    #     setheader('Content-Disposition', 'inline; filename=%s' % filename)
    #     RESPONSE.write(result)
    #     return

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
        self.invokeFactory(id=invoice_id, type_name='Invoice')
        invoice = self._getOb(invoice_id)
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
                lineitem['ClientOrderNumber'] = item.getClientOrderNumber()
                item_description = get_invoice_item_description(item)
                l = [item.getRequestID(), item_description]
                description = ' '.join(l)
            elif item.portal_type == 'SupplyOrder':
                lineitem['ItemDate'] = item.getDateDispatched()
                description = item.getOrderNumber()
            lineitem['ItemDescription'] = description
            lineitem['Subtotal'] = '%0.2f' % item.getSubtotal()
            lineitem['VATTotal'] = '%0.2f' % item.getVATTotal()
            lineitem['Total'] = '%0.2f' % item.getTotal()
            invoice.invoice_lineitems.append(lineitem)
        invoice.reindexObject()

    security.declarePublic('current_date')

    def current_date(self):
        """ return current date """
        return DateTime()

    def guard_cancel_transition(self):
        return True

    def guard_reinstate_transition(self):
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
