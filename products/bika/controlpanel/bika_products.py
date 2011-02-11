from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from zope.interface.declarations import implements

class LabProductsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabProduct'}
    content_add_buttons = ['LabProduct']
    title = "Lab Products"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False

    columns = {
               'title_or_id': {'title': 'Title'},
               'Volume': {'title': 'Volume'},
               'Unit': {'title': 'Unit'},
               'Price': {'title': 'Price'},
               'VATAmount': {'title': 'VAT Amount'},
               'TotalPrice': {'title': 'Total Price'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['title_or_id', 'Volume', 'Unit', 'Price', 'VATAmount', 'TotalPrice'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['Volume'] = obj.Volume()
            items[x]['Unit'] = obj.Unit()
            items[x]['Price'] = obj.Price()
            items[x]['VATAmount'] = obj.VATAmount()
            items[x]['TotalPrice'] = obj.TotalPrice()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items
