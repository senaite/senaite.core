from Products.CMFCore import permissions
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface.declarations import implements

class LabContactsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabContact'}
    content_add_buttons = ['LabContact']
    batch = True
    title = "Lab Contacts"
    description = ""
    b_size = 100
    full_objects = False
    columns = {
               'title_or_id': {'title': 'Title'},
               'Department': {'title': 'Department'},
               'BusinessPhone': {'title': 'Phone'},
               'Fax': {'title': 'Fax'},
               'MobilePhone': {'title': 'Mobile Phone'},
               'EmailAddress': {'title': 'Email Address'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['title_or_id', 'Department', 'BusinessPhone', 'Fax', 'MobilePhone', 'EmailAddress'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['Department'] = obj.Department
            items[x]['BusinessPhone'] = obj.BusinessPhone
            items[x]['Fax'] = obj.BusinessFax
            items[x]['MobilePhone'] = obj.MobilePhone
            items[x]['EmailAddress'] = obj.EmailAddress
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items
