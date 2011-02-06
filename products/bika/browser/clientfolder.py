from Products.CMFCore.utils import getToolByName
from Products.bika import logger
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.interfaces import IClientFolderView
from zope.interface import implements

class ClientFolderContentsView(BikaFolderContentsView):
    implements(IClientFolderView)
    allowed_content_types = ['Client', ]

    def __init__(self, context, request):
        super(ClientFolderContentsView, self).__init__(context, request)
        self.portal_types = getToolByName(self.context, 'portal_types')

    content_add_buttons = ['Client', ]
    contentFilter = {'portal_type': 'Client'}
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'title_or_id': {'title': 'Name', 'field': 'title_or_id'},
               'getEmailAddress': {'title': 'Email Address', 'field':'getEmailAddress'},
               'getPhone': {'title': 'Phone', 'field':'getPhone'},
               'getFax': {'title': 'Fax', 'field':'getFax'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns':['title_or_id',
                                'getEmailAddress',
                                'getPhone',
                                'getFax', ]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'title_or_id': items[x]['url']}

        return items
