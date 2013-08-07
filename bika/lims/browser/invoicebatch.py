from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _

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
            'vattotal': {'title': _('VAT')},
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
                    'vattotal',
                    'total',
                ],
            },
        ]

    def getInvoices(self, contentFilter):
        return self.context.objectValues('Invoice')

    def folderitems(self):
        self.contentsMethod = self.getInvoices
        items = BikaListingView.folderitems(self)
        for item in items:
            obj = item['obj']
            number_link = "<a href='%s'>%s</a>" % (
                item['url'], obj.getId()
            )
            item['replace']['id'] = number_link
            item['client'] = obj.getClient().Title()
            item['invoicedate'] = self.ulocalized_time(obj.getInvoiceDate())
            item['subtotal'] = obj.getSubtotal()
            item['vattotal'] = obj.getVATTotal()
            item['total'] = obj.getTotal()
        return items
