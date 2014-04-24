from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from Products.CMFPlone.utils import getToolByName
from bika.lims.permissions import AddInvoice
from bika.lims.permissions import ManageInvoices
from bika.lims.utils import currency_format


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

    def folderitems(self):
        currency = currency_format(self.context, 'en')
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
            item['subtotal'] = currency(obj.getSubtotal())
            item['vattotal'] = currency(obj.getVATTotal())
            item['total'] = currency(obj.getTotal())
        return items
