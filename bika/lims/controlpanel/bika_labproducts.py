from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from bika.lims.interfaces import ILabProducts

class LabProductsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabProduct'}
    content_add_actions = {_('Product'): "createObject?type_name=LabProduct"}
    title = _("Lab Products")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 20

    columns = {
               'title': {'title': _('Title')},
               'Volume': {'title': _('Volume')},
               'Unit': {'title': _('Unit')},
               'Price': {'title': _('Price')},
               'VATAmount': {'title': _('VAT Amount')},
               'TotalPrice': {'title': _('Total Price')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['title', 'Volume', 'Unit', 'Price', 'VATAmount', 'TotalPrice'],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['Volume'] = obj.Volume
            items[x]['Unit'] = obj.Unit
            items[x]['Price'] = obj.Price
            items[x]['VATAmount'] = obj.getVATAmount()
            items[x]['TotalPrice'] = obj.getTotalPrice()
            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

schema = ATFolderSchema.copy()
class LabProducts(ATFolder):
    implements(ILabProducts)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabProducts, PROJECTNAME)
