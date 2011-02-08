from Products.CMFCore.utils import getToolByName
from Products.bika import logger
from Products.bika.browser.bika_list import BikaListView
from Products.bika.interfaces import IClientFolderView
from zope.interface import implements

class ClientFolderContentsView(BikaListView):
    implements(IClientFolderView)

    title = "Clients"
    description = ""
    content_add_buttons = ['Client', ]
    contentFilter = {'portal_type': 'Client'}
    batch = True
    b_size = 100
    full_objects = False
    show_editable_border = False

    columns = {
               'title_or_id': {'title': 'Name', 'field': 'title_or_id'},
               'getEmailAddress': {'title': 'Email Address', 'field':'getEmailAddress'},
               'getPhone': {'title': 'Phone', 'field':'getPhone'},
               'getFax': {'title': 'Fax', 'field':'getFax'},
              }

    buttons = {
               'delete': {'cssclass': 'context',
                          'title': 'Delete',
                          'url': 'folder_delete:method'},
              }

    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns':['title_or_id',
                                'getEmailAddress',
                                'getPhone',
                                'getFax', ],
                     'buttons':[buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaListView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'title_or_id': items[x]['url']}

        return items

    def __call__(self):
        return self.template()
