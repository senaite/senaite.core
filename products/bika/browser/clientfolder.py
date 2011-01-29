from Products.bika import logger
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.interfaces import IClientFolderView
from zope.interface import implements

class ClientFolderContentsView(BikaFolderContentsView):
    implements(IClientFolderView)
    contentFilter = {'portal_type': 'Client'}
    batch = True
    b_size = 100
    full_objects = False
    columns = [
              {'title': 'Title', 'field':'title_or_id'},
              {'title': 'Email Address', 'field':'getEmailAddress'},
              {'title': 'Phone', 'field':'getPhone'},
              {'title': 'Fax', 'field':'getFax'},
             ]

    # contentactions.pt
    object_actions = [{'id': 'add_client', 'title':'Add Client', 'url':'xxx', 'icon':'client.png'},
                     ]
