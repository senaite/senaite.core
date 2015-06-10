from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import currency_format
import csv
from cStringIO import StringIO

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


class BatchFolderExportCSV(InvoiceBatchInvoicesView):

    def __call__(self, REQUEST, RESPONSE):
        """
        Export invoice batch into csv format.
        Writes the csv file into the RESPONSE to allow
        the file to be streamed to the user.
        Nothing gets returned.
        """

        delimiter = ','
        filename = 'invoice_batch.txt'
        # Getting the invoice batch
        container = self.context
        assert container
        container.plone_log("Exporting InvoiceBatch to CSV format for PASTEL")
        # Getting the invoice batch's invoices
        invoices = self.getInvoices({})
        if not len(invoices):
            container.plone_log("InvoiceBatch contains no entries")

        csv_rows = [['Invoice Batch']]
        # Invoice batch header
        csv_rows.append(['ID', container.getId()])
        csv_rows.append(['Invoice Batch Title', container.title])
        csv_rows.append(['Start Date', container.getBatchStartDate().strftime('%Y-%m-%d')])
        csv_rows.append(['End Date', container.getBatchEndDate().strftime('%Y-%m-%d')])
        csv_rows.append([])

        # Building the invoice field header
        csv_rows.append(['Invoices'])
        csv_rows.append(['Invoice ID', 'Client ID', 'Client Name', 'Account Num.', 'Phone', 'Date', 'Total Price'])
        invoices_items_rows = []
        for invoice in invoices:
            # Building the invoice field header
            invoice_info_header = [invoice.getId(),
                                   invoice.getClient().getId(),
                                   invoice.getClient().getName(),
                                   invoice.getClient().getAccountNumber(),
                                   invoice.getClient().getPhone(),
                                   invoice.getInvoiceDate().strftime('%Y-%m-%d'),
                                   ]
            csv_rows.append(invoice_info_header)
            # Obtaining and sorting all analysis items. These analysis are saved inside a list to add later
            items = invoice.invoice_lineitems
            mixed = [(item.get('OrderNumber', ''), item) for item in items]
            mixed.sort()
            # Defining each analysis row
            for line in mixed:
                invoice_analysis = [line[1].get('ItemDate', ''),
                                    line[1].get('ItemDescription', ''),
                                    line[1].get('OrderNumber', ''),
                                    line[1].get('Subtotal', ''),
                                    line[1].get('VATAmount', ''),
                                    line[1].get('Total', ''),
                                    ]
                invoices_items_rows.append(invoice_analysis)

        csv_rows.append([])
        # Creating analysis items header
        csv_rows.append(['Invoices items'])
        csv_rows.append(['Date', 'Description', 'Order', 'Amount', 'VAT', 'Amount incl. VAT'])
        # Adding all invoices items
        for item_row in invoices_items_rows:
            csv_rows.append(item_row)

        # convert lists to csv string
        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter=delimiter)
        assert writer
        writer.writerows(csv_rows)
        result = ramdisk.getvalue()
        ramdisk.close()
        # stream file to browser
        setheader = RESPONSE.setHeader
        setheader('Content-Length', len(result))
        setheader('Content-Type',
            'text/x-comma-separated-values')
        setheader('Content-Disposition', 'inline; filename=%s' % filename)
        RESPONSE.write(result)
