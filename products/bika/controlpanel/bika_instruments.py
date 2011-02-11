from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from zope.interface.declarations import implements

class InstrumentsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Instrument'}
    content_add_buttons = ['Instrument']
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'title_or_id': {'title': 'Title'},
               'Type': {'title': 'Type'},
               'Brand': {'title': 'Brand'},
               'Model': {'title': 'Model'},
               'ExpireyDate': {'title': 'Expiry Date'},
              }
    wflist_states = [
                    {'title_or_id': 'All', 'id':'all',
                     'columns': ['title_or_id', 'Type', 'Brand', 'Model', 'ExpiryDate'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['Type'] = obj.Type()
            items[x]['Brand'] = obj.Brand()
            items[x]['Model'] = obj.Model()
            items[x]['ExpiryDate'] = obj.ExpiryDate()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items
