from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from zope.interface.declarations import implements

class StandardManufacturersView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'StandardManufacturer'}
    content_add_buttons = ['StandardManufacturer']
    title = "Standard Manufacturers"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'title_or_id': {'title': 'Title'},
               'StandardManufacturerDescription': {'title': 'Description'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['title_or_id', 'StandardManufacturerDescription'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['StandardManufacturerDescription'] = obj.StandardManufacturerDescription()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items
