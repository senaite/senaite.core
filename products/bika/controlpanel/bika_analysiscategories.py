from plone.app.content.browser.interfaces import IFolderContentsView
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from zope.interface.declarations import implements

class AnalysisCategoriesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisCategory'}
    content_add_buttons = ['AnalysisCategory']
    title = "Analysis Categories"
    description = ""
    batch = True
    b_size = 100
    show_editable_border = False
    full_objects = False
    columns = {
               'title_or_id': {'title': 'Title'},
               'CategoryDescription': {'title': 'Category Description'},
               'Department': {'title': 'Department'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['title_or_id', 'CategoryDescription', 'Department'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['CategoryDescription'] = obj.CategoryDescription()
            items[x]['Department'] = obj.getDepartment().Title()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/edit",
                                 'Department': obj.getDepartment().absolute_url()}
        return items
