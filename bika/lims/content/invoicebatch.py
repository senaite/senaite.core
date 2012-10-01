"""InvoiceBatch is a container for Invoice instances.
"""
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore  import permissions
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PostInvoiceBatch, ManageInvoices, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IInvoiceBatch
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    DateTimeField('BatchStartDate',
        required = 1,
        default_method = 'current_date',
        widget = CalendarWidget(
            label = _("Batch start date"),
        ),
    ),
    DateTimeField('BatchEndDate',
        required = 1,
        default_method = 'current_date',
        widget = CalendarWidget(
            label = _("Batch end date"),
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

    security.declareProtected(ManageInvoices, 'invoicebatch_export')
    def invoicebatch_export(self, REQUEST, RESPONSE):
        """ Export invoice batch in csv format.
        Writes the csv file into the RESPONSE to allow
        the file to be streamed to the user.
        Nothing gets returned.
        """
        import csv
        from cStringIO import StringIO
        delimiter = ','
        filename = 'batch.txt'

        container = self.unrestrictedTraverse(REQUEST.get('current_path'))
        assert(container)

        container.plone_log("Exporting InvoiceBatch to CSV format for PASTEL")
        invoices = container.listFolderContents()

        if (not len(invoices)):
            container.plone_log("InvoiceBatch contains no entries")

        rows = []
        _ordNum = 'starting at none'
        for invoice in invoices:
            new_invoice = True
            _invNum = "%s" % invoice.getInvoiceNumber()[:8]
            _clientNum = "%s" % invoice.getClient().getAccountNumber()
            _invDate = "%s" % invoice.getInvoiceDate().strftime('%Y-%m-%d')
            _monthNum = invoice.getInvoiceDate().month()
            if _monthNum < 7:
                _periodNum = _monthNum + 6
            else:
                _periodNum = _monthNum - 6
            _periodNum = "%s" % _monthNum

            _message1 = ''
            _message2 = ''
            _message3 = ''

            items = invoice.objectValues('InvoiceLineItem')
            mixed = [(item.getClientOrderNumber(), item) for item in items]
            mixed.sort()
            lines = [t[1] for t in mixed]

            #iterate through each invoice line
            for line in lines:
                if new_invoice or line.getClientOrderNumber() != _ordNum:
                    new_invoice = False
                    _ordNum = line.getClientOrderNumber()

                    #create header csv entry as a list
                    header = [ \
                        "Header", _invNum, " ", " ", _clientNum, _periodNum, \
                        _invDate, _ordNum, "N", 0, _message1, _message2, \
                        _message3, "", "", "", "", "", "", 0, "", "", "", "", \
                        0, "", "", "N"]
                    rows.append(header)


                _quant = 1
                _unitp = line.getSubtotal()
                _inclp = line.getTotal()
                _item = line.getItemDescription()
                _desc = "Analysis: %s" % _item[:40]
                if _item.startswith('Water') or _item.startswith('water'):
                    _icode = "002"
                else:
                    _icode = "001"
                _ltype = "4"
                _ccode = ""

                #create detail csv entry as a list
                detail = ["Detail", 0, _quant, _unitp, _inclp, \
                          "", "01", "0", "0", _icode, _desc, \
                          _ltype, _ccode, ""]
                rows.append(detail)

        #convert lists to csv string
        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter = delimiter)
        assert(writer)

        writer.writerows(rows)
        result = ramdisk.getvalue()
        ramdisk.close()

        #stream file to browser
        setheader = RESPONSE.setHeader
        setheader('Content-Length', len(result))
        setheader('Content-Type',
            'text/x-comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        RESPONSE.write(result)

        return

    security.declareProtected(ManageInvoices, 'invoices')
    def invoices(self):
        return self.objectValues('Invoice')

    security.declareProtected(PostInvoiceBatch, 'post')
    def post(self, REQUEST = None):
        """ Post invoices
        """
        map (lambda e: e._post(), self.invoices())
        if REQUEST:
            REQUEST.RESPONSE.redirect('invoicebatch_invoices')

    security.declareProtected(ManageInvoices, 'create_batch')
    def create_batch(self):
        """ Create batch invoices
        """
        # query for ARs in date range
        query = {
            'portal_type': 'AnalysisRequest',
            'review_state': 'published',
            'getInvoiceExclude': False,
            'getDatePublished': {
                'range': 'min:max',
                'query': [self.getBatchStartDate(),
                          self.getBatchEndDate()]
                }
        }
        ars = self.bika_catalog(query)

        ## query for Orders in date range
        query = {
            'portal_type': 'SupplyOrder',
            'review_state': 'dispatched',
            'getDateDispatched': {
                'range': 'min:max',
                'query': [self.getBatchStartDate(),
                          self.getBatchEndDate()]
                }
        }
        orders = self.portal_catalog(query)
        #orders = ()

        # make list of clients from found ARs and Orders
        clients = {}
        for rs in (ars, orders):
            for p in rs:
                obj = p.getObject()
                if obj.Invoiced():
                    continue
                client_uid = obj.aq_parent.UID()
                l = clients.get(client_uid, [])
                l.append(obj)
                clients[client_uid] = l

        # create an invoice for each client
        for client_uid, items in clients.items():
            self.createInvoice(client_uid, items)

        self.REQUEST.RESPONSE.redirect('invoicebatch_invoices')


    security.declareProtected(ManageInvoices, 'createInvoice')
    def createInvoice(self, client_uid, items):
        """ Create an item in an invoice batch
        """
        # create an invoice for each client
        invoice_id = self.generateUniqueId('Invoice')
        self.invokeFactory(id = invoice_id, type_name = 'Invoice')
        invoice = self._getOb(invoice_id)
        invoice.edit(
            Client = client_uid,
            InvoiceNumber = invoice_id,
            InvoiceDate = DateTime(),
        )
        invoice.processForm()
        for item in items:
            lineitem_id = self.generateUniqueId(
                'InvoiceLineItem')
            invoice.invokeFactory(id=lineitem_id, type_name='InvoiceLineItem')
            lineitem = invoice._getOb(lineitem_id)
            if item.portal_type == 'AnalysisRequest':
                lineitem.setItemDate(item.getDatePublished())
                lineitem.setClientOrderNumber(item.getClientOrderNumber())
                item_description = self.get_invoice_item_description(item)
                l = [item.getRequestID(), item_description]
                description = ' '.join(l)
            elif item.portal_type == 'SupplyOrder':
                lineitem.setItemDate(item.getDateDispatched())
                description = item.getOrderNumber()
            lineitem.setItemDescription(description)
            lineitem.setSubtotal(item.getSubtotal())
            lineitem.setVAT(item.getVAT())
            lineitem.setTotal(item.getTotal())
            lineitem.reindexObject()
            item.setInvoice(invoice)
            lineitem.processForm()
        invoice.reindexObject()

        return

    security.declareProtected(permissions.ModifyPortalContent,
                              'processForm')
    def processForm(self, data = 1, metadata = 0, REQUEST = None, values = None):
        """ Override BaseObject.processForm so that we can perform setup
            task once the form is filled in
        """
        BaseFolder.processForm(self, data = data, metadata = metadata,
            REQUEST = REQUEST, values = values)
        self.create_batch()

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

registerType(InvoiceBatch, PROJECTNAME)
