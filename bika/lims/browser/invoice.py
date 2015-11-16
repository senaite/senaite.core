from bika.lims.browser import BrowserView
from bika.lims.interfaces import IInvoiceView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n.locales import locales
from zope.interface import implements


class InvoiceView(BrowserView):

    implements(IInvoiceView)

    template = ViewPageTemplateFile("templates/invoice.pt")
    content = ViewPageTemplateFile("templates/invoice_content.pt")

    def __init__(self, context, request):
        super(InvoiceView, self).__init__(context, request)
        request.set('disable_border', 1)

    def __call__(self):
        context = self.context
        workflow = getToolByName(context, 'portal_workflow')
        # Gather relted objects
        batch = context.aq_parent
        client = context.getClient()
        analysis_request = context.getAnalysisRequest() if context.getAnalysisRequest() else None
        # Gather general data
        self.invoiceId = context.getId()
        self.invoiceDate = self.ulocalized_time(context.getInvoiceDate())
        self.subtotal = '%0.2f' % context.getSubtotal()
        self.VATAmount = '%0.2f' % context.getVATAmount()
        self.total = '%0.2f' % context.getTotal()
        # Create the batch range
        start = self.ulocalized_time(batch.getBatchStartDate())
        end = self.ulocalized_time(batch.getBatchEndDate())
        self.batchRange = "%s to %s" % (start, end)
        # Gather client data
        self.clientName = client.Title()
        self.clientURL = client.absolute_url()
        self.clientPhone = client.getPhone()
        self.clientFax = client.getFax()
        self.clientEmail = client.getEmailAddress()
        self.clientAccountNumber = client.getAccountNumber()
        # currency info
        locale = locales.getLocale('en')
        self.currency = self.context.bika_setup.getCurrency()
        self.symbol = locale.numbers.currencies[self.currency].symbol
        # Get an available client address in a preferred order
        self.clientAddress = None
        # A list with the items and its invoice values to render in template
        self.items = []
        addresses = (
            client.getBillingAddress(),
            client.getPostalAddress(),
            client.getPhysicalAddress(),
        )
        for address in addresses:
            if address.get('address'):
                self.clientAddress = address
                break
        # Gather the line items
        items = context.invoice_lineitems
        for item in items:
            invoice_data = {
                'invoiceDate': self.ulocalized_time(item.get('ItemDate', '')),
                'description': item.get('ItemDescription', ''),
                'orderNo': item.get('OrderNumber', ''),
                'subtotal': '%0.2f' % item.get('Subtotal', ''),
                'VATAmount': '%0.2f' % item.get('VATAmount', ''),
                'total': '%0.2f' % item.get('Total', ''),
            }
            if item.get('AnalysisRequest', ''):
                    invoice_data['orderNoURL'] = item['AnalysisRequest'].absolute_url()
            elif item.get('SupplyOrder', ''):
                    invoice_data['orderNoURL'] = item['SupplyOrder'].absolute_url()
            else:
                invoice_data['orderNoURL'] = ''
            self.items.append(invoice_data)
        # Render the template
        return self.template()


class InvoicePrintView(InvoiceView):

    template = ViewPageTemplateFile("templates/invoice_print.pt")

    def __call__(self):
        return InvoiceView.__call__(self)
