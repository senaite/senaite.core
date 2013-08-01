from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import AddInvoice
from bika.lims.permissions import ManageInvoices
from plone.app.content.browser.interfaces import IFolderContentsView
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


class InvoiceFolderContentsView(BikaListingView):

    implements(IFolderContentsView)

    def __init__(self, context, request):
        super(InvoiceFolderContentsView, self).__init__(context, request)
        self.contentFilter = {}
        self.icon = self.portal_url + "/++resource++bika.lims.images/invoice_big.png"
        self.title = _("Invoices")
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 25
        request.set('disable_border', 1)
        self.columns = {
            'title': {'title': _('Title')},
            'start': {'title': _('Batch Start Date')},
            'end': {'title': _('Batch End Date')},
        }
        self.review_states = [
            {
                'id': 'default',
                'contentFilter': {},
                'title': _('Default'),
                'transitions': [],
                'columns': ['title', 'start', 'end'],
            },
        ]


    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if (mtool.checkPermission(AddInvoice, self.context)):
            self.context_actions[_('Add')] = {
                'url': 'createObject?type_name=InvoiceBatch',
                'icon': '++resource++bika.lims.images/add.png'
            }
        if mtool.checkPermission(ManageInvoices, self.context):
            self.show_select_column = True
        return super(InvoiceFolderContentsView, self).__call__()

    def getInvoiceBatches(self, contentFilter):
        return self.context.objectValues('InvoiceBatch')

    def folderitems(self):
        self.contentsMethod = self.getInvoiceBatches
        items = BikaListingView.folderitems(self)
        for item in items:
            obj = item['obj']
            title_link = "<a href='%s'>%s</a>" % (item['url'], item['title'])
            item['replace']['title'] = title_link
            item['start'] = self.ulocalized_time(obj.getBatchStartDate())
            item['end'] = self.ulocalized_time(obj.getBatchEndDate())
        return items

