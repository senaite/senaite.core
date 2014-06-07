from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.utils import t
from operator import itemgetter
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class SupplyOrderFolderView(BikaListingView):

    implements(IViewView)

    def __init__(self, context, request):
        super(SupplyOrderFolderView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'SupplyOrder',
            'sort_on': 'sortable_title',
            'sort_order': 'reverse',
        }
        self.context_actions = {}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url
        self.show_table_only = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.form_id = 'orders'
        self.icon = self.portal_url + '/++resource++bika.lims.images/supplyorder_big.png'
        self.title = _('Orders')
        self.columns = {
            'OrderNumber': {'title': _('Order Number')},
            'OrderDate': {'title': _('Order Date')},
            'DateDispatched': {'title': _('Date Dispatched')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {
                'id': 'default',
                'title': _('All'),
                'contentFilter': {},
                'columns': [
                    'OrderNumber',
                    'OrderDate',
                    'DateDispatched',
                    'state_title'
                ]
            }, {
                'id': 'pending',
                'contentFilter': {'review_state':'pending'},
                'title': _('Pending'),
                'columns': ['OrderNumber', 'OrderDate']
            }, {
                'id': 'dispatched',
                'contentFilter': {'review_state':'dispatched'},
                'title': _('Dispatched'),
                'columns': [
                    'OrderNumber',
                    'OrderDate',
                    'DateDispatched'
                ]
            },
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        items.sort(key=itemgetter('OrderDate'), reverse=True)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['OrderNumber'] = obj.getOrderNumber()
            items[x]['OrderDate'] = self.ulocalized_time(obj.getOrderDate())
            items[x]['DateDispatched'] = self.ulocalized_time(obj.getDateDispatched())
            items[x]['replace']['OrderNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['OrderNumber'])
        return items
