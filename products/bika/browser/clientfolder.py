from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface import implements

class ClientFolderContentsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Client'}
    content_add_buttons = {'Client': "createObject?type_name=Client"}
    title = "Clients"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100

    columns = {
               'title_or_id': {'title': 'Name'},
               'getEmailAddress': {'title': 'Email Address'},
               'getPhone': {'title': 'Phone'},
               'getFax': {'title': 'Fax'},
              }

    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns':['title_or_id',
                                'getEmailAddress',
                                'getPhone',
                                'getFax', ],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {
                'title_or_id': items[x]['url'],
                'getEmailAddress': items[x]['getEmailAddress'] and 'mailto:%s' % items[x]['getEmailAddress'] or "",
            }

        return items

    def __call__(self):
        return self.template()
