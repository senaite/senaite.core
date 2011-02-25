from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.interface.declarations import implements

class DepartmentsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Department'}
    content_add_buttons = ['Department']
    title = "Lab Departments"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    show_editable_border = False
    columns = {
               'title_or_id': {'title': 'Title'},
               'DepartmentDescription': {'title': 'Department Description'},
               'Manager': {'title': 'Manager'},
               'ManagerPhone': {'title': 'Manager Phone'},
               'ManagerEmail': {'title': 'Manager Email'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['title_or_id', 'DepartmentDescription', 'Manager', 'ManagerPhone', 'ManagerEmail'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['DepartmentDescription'] = obj.DepartmentDescription()
            items[x]['Manager'] = obj.getManagerName()
            if items[x]['Manager']:
                items[x]['ManagerPhone'] = obj.getManager().BusinessPhone
                items[x]['ManagerEmail'] = obj.getManager().EmailAddress
            else:
                items[x]['ManagerPhone'] = ""
                items[x]['ManagerEmail'] = ""

            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit",
                                 'Manager': obj.getManager().absolute_url() + "/edit",
                                 'ManagerEmail': "mailto:%s" % (items[x]['ManagerEmail'])}

        return items
