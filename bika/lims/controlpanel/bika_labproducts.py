from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from bika.lims.interfaces import ILabProducts

class LabProductsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(LabProductsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'LabProduct',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=LabProduct',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Lab Products"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/product_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Title'),
                      'index': 'sortable_title',
                      'toggle': True},
            'Volume': {'title': _('Volume'),
                       'index': 'getVolume',
                       'toggle': True},
            'Unit': {'title': _('Unit'),
                       'index': 'getUnit',
                       'toggle': True},
            'Price': {'title': _('Price'),
                       'index': 'getPrice',
                       'toggle': True},
            'VATAmount': {'title': _('VAT Amount'),
                       'index': 'getVATAmount',
                       'toggle': True},
            'TotalPrice': {'title': _('Total Price'),
                       'index': 'getTotalPrice',
                       'toggle': True},
        }
        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Volume',
                         'Unit',
                         'Price',
                         'VATAmount',
                         'TotalPrice']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Volume',
                         'Unit',
                         'Price',
                         'VATAmount',
                         'TotalPrice']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Volume',
                         'Unit',
                         'Price',
                         'VATAmount',
                         'TotalPrice']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Volume'] = obj.getVolume()
            items[x]['Unit'] = obj.getUnit()
            items[x]['Price'] = obj.getPrice()
            items[x]['VATAmount'] = obj.getVATAmount()
            items[x]['TotalPrice'] = obj.getTotalPrice()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

schema = ATFolderSchema.copy()
class LabProducts(ATFolder):
    implements(ILabProducts)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabProducts, PROJECTNAME)
