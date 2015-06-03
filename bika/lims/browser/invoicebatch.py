from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from Products.CMFPlone.utils import getToolByName
from bika.lims.permissions import AddInvoice
from bika.lims.permissions import ManageInvoices
from bika.lims.utils import currency_format
from bika.lims.browser import BrowserView


class InvoiceBatchInvoicesView(BikaListingView):

    def __init__(self, context, request):
        super(InvoiceBatchInvoicesView, self).__init__(context, request)
        self.contentFilter = {}
        self.title = context.Title()
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 25
        request.set('disable_border', 1)
        self.context_actions = {}
        self.columns = {
            'id': {'title': _('Invoice Number')},
            'client': {'title': _('Client')},
            'invoicedate': {'title': _('Invoice Date')},
            'subtotal': {'title': _('Subtotal')},
            'vatamount': {'title': _('VAT')},
            'total': {'title': _('Total')},
        }
        self.review_states = [
            {
                'id': 'default',
                'contentFilter': {},
                'title': _('Default'),
                'transitions': [],
                'columns': [
                    'id',
                    'client',
                    'invoicedate',
                    'subtotal',
                    'vatamount',
                    'total',
                ],
            },
        ]

    def getInvoices(self, contentFilter):
        return self.context.objectValues('Invoice')

    # def __call__(self):
    #     mtool = getToolByName(self.context, 'portal_membership')
    #     addPortalMessage = self.context.plone_utils.addPortalMessage
    #     if mtool.checkPermission(AddInvoice, self.context):
    #         clients = self.context.clients.objectIds()
    #         if clients:
    #             self.context_actions[_('Add')] = {
    #                 'url': 'createObject?type_name=Invoice',
    #                 'icon': '++resource++bika.lims.images/add.png'
    #             }
    #     return super(InvoiceBatchInvoicesView, self).__call__()

    def folderitems(self, full_objects=False):
        currency = currency_format(self.context, 'en')
        self.show_all = True
        self.contentsMethod = self.getInvoices
        items = BikaListingView.folderitems(self, full_objects)
        for item in items:
            obj = item['obj']
            number_link = "<a href='%s'>%s</a>" % (
                item['url'], obj.getId()
            )
            item['replace']['id'] = number_link
            item['client'] = obj.getClient().Title()
            item['invoicedate'] = self.ulocalized_time(obj.getInvoiceDate())
            item['subtotal'] = currency(obj.getSubtotal())
            item['vatamount'] = currency(obj.getVATAmount())
            item['total'] = currency(obj.getTotal())
        return items


class BatchFolderExportCSV(BrowserView):

    def __call__(self, REQUEST, RESPONSE):
        """
        Export invoice batch into csv format.
        Writes the csv file into the RESPONSE to allow
        the file to be streamed to the user.
        Nothing gets returned.
        """
        import pdb;pdb.set_trace()
        import csv
        from cStringIO import StringIO
        delimiter = ','
        filename = 'batch.txt'

        container = self.unrestrictedTraverse(REQUEST.get('current_path'))
        assert container

        container.plone_log("Exporting InvoiceBatch to CSV format for PASTEL")
        invoices = container.listFolderContents()

        if not len(invoices):
            container.plone_log("InvoiceBatch contains no entries")

        rows = []
        _ordNum = 'starting at none'
        for invoice in invoices:
            new_invoice = True
            _invNum = "%s" % invoice.getId()[:8]
            _clientNum = "%s" % invoice.getClient().getAccountNumber()
            _invDate = "%s" % invoice.getInvoiceDate().strftime('%Y-%m-%d')
            _monthNum = invoice.getInvoiceDate().month()
            if _monthNum < 7:
                _periodNum = _monthNum + 6
            else:
                _periodNum = _monthNum - 6
            _periodNum = "%s" % _monthNum
        import pdb;pdb.set_trace()
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

