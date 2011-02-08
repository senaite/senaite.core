from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from Products.bika.browser.bika_list import BikaListView
from zope.interface.declarations import implements

class AnalysisCategories(BikaListView):
    implements(IFolderContentsView)
    content_add_buttons = ['AnalysisCategory', ]
    contentFilter = {'portal_type': 'AnalysisCategory'}
    title = "Analysis Categories"
    description = ""
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = []
    columns = {
               'CategoryDescription': {'title': 'Category Description'},
               'Department': {'title': 'Department'},
              }
    buttons = {
               'delete': {'cssclass': 'context',
                          'title': 'Delete',
                          'url': 'folder_delete:method'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns':['CategoryDescription', 'Department'],
                     'buttons':[buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaListView.folderitems(self)
        for x in range(len(items)):
            obj = items[x].getObject()
            items[x]['CategoryDescription'] = obj.CategoryDescription
            items[x]['Department'] = obj.Department
            items[x]['links'] = {'CategoryDescription': items[x]['url']}

        return items
