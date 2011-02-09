from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from zope.interface.declarations import implements

class AnalysisCategoriesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisCategory'}
    content_add_buttons = ['AnalysisCategory']
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'CategoryDescription': {'title': 'CategoryDescription', 'icon':'category.png'},
               'Department': {'title': 'Department'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['CategoryDescription', 'Department'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['CategoryDescription'] = obj.CategoryDescription()
            items[x]['Department'] = obj.getDepartment().Title()
            items[x]['links'] = {'CategoryDescription': items[x]['url'],
                                 'Department': obj.getDepartment().absolute_url()}

        return items
