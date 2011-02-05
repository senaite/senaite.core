from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from zope.interface.declarations import implements

class AnalysisCategories(BikaFolderContentsView):
    implements(IFolderContentsView)
    allowed_content_types = ['AnalysisCategory']
    contentFilter = {'portal_type': 'AnalysisCategory'}
    batch = True
    b_size = 100
    full_objects = False
    wflist_states = []
    columns = {
               'title': {'title': 'Title'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['title']},
                    ]

    def __init__(self, context, request):
        super(BikaFolderContentsView, self).__init__(context, request)
        self.context.allowed_content_types = self.allowed_content_types

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'title': items[x]['url']}

        return items
