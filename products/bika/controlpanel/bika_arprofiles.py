from plone.app.content.browser.interfaces import IFolderContentsView
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from zope.interface.declarations import implements

class ARProfilesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabARProfile'}
    content_add_buttons = ['LabARProfile']
    title = "Analysis Request Templates"
    description = ""
    batch = True
    b_size = 100
    show_editable_border = False
    full_objects = False
    columns = {
               'title_or_id': {'title': 'Title'},
               'ProfileKey': {'title': 'Profile Key'},
              }
    wflist_states = [
                    {'title_or_id': 'All', 'id':'all',
                     'columns': ['title_or_id', 'ProfileKey'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit"}

        return items
