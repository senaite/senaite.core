from bika.lims import bikaMessageFactory as _
from bika.lims.browser.supplyorderfolder import SupplyOrderFolderView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class ClientOrdersView(SupplyOrderFolderView):
    implements(IViewView)

    def __init__(self, context, request):
        super(ClientOrdersView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'SupplyOrder',
            'sort_on': 'sortable_title',
            'sort_order': 'reverse',
            'path': {
                'query': '/'.join(context.getPhysicalPath()),
                'level': 0
            }
        }
        self.context_actions = {
            _('Add'): {
                'url': 'createObject?type_name=SupplyOrder',
                'icon': '++resource++bika.lims.images/add.png'
            }
        }
