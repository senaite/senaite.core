from Products.CMFCore.utils import getToolByName
from Products.bika import logger
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.interfaces import IClientFolderView
from zope.interface import implements

class ClientFolderContentsView(BikaFolderContentsView):
    implements(IClientFolderView)

    def __init__(self, context, request):
        super(ClientFolderContentsView, self).__init__(context, request)

    allowed_content_types = ['Client', ]
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
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'title_or_id': items[x]['url']}

        return items

    def __call__(self):
        return self.template()
