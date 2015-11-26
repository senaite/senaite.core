from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
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
        self.catalog = "portal_catalog"
        self.contentFilter = {'portal_type': 'InvoiceBatch'}
        self.icon = self.portal_url + "/++resource++bika.lims.images/invoice_big.png"
        self.title = self.context.translate(_("Statements"))
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 25
        request.set('disable_border', 1)
        self.columns = {
            'title': {'title': _('Title')},
            'start': {'title': _('Start Date')},
            'end': {'title': _('End Date')},
        }
        self.review_states = [
            {
                'id': 'default',
                'contentFilter': {'cancellation_state': 'active'},
                'title': _('Active'),
                'transitions': [{'id': 'cancel'}],
                'columns': ['title', 'start', 'end'],
            },
            {
                'id': 'cancelled',
                'contentFilter': {'cancellation_state': 'cancelled'},
                'title': _('Cancelled'),
                'transitions': [{'id': 'reinstate'}],
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

    def getInvoiceBatches(self, contentFilter={}):
        wf = getToolByName(self.context, 'portal_workflow')
        desired_state = contentFilter.get('cancellation_state', 'active')
        values = self.context.objectValues()
        return [ib for ib in values if
                wf.getInfoFor(ib, 'cancellation_state') == desired_state]

    def folderitems(self):
        self.contentsMethod = self.getInvoiceBatches
        items = BikaListingView.folderitems(self)
        for x, item in enumerate(items):
            if 'obj' not in item:
                continue
            obj = item['obj']
            title_link = "<a href='%s'>%s</a>" % (item['url'], item['title'])
            items[x]['replace']['title'] = title_link
            items[x]['start'] = self.ulocalized_time(obj.getBatchStartDate())
            items[x]['end'] = self.ulocalized_time(obj.getBatchEndDate())

        return items
