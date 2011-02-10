from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from zope.interface.declarations import implements

class AnalysisSpecsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisSpec'}
    content_add_buttons = ['AnalysisSpec']
    title = "Analysis Specs"
    description = "Set up the laboratory analysis service results specifications"
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'SampleType': {'title': 'SampleType', 'icon':'analysisspec.png'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['SampleType'],
                     'buttons':[BikaFolderContentsView.default_buttons['delete']]},
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            obj = items[x]['obj'].getObject()
            items[x]['SampleType'] = obj.SampleType()
            items[x]['links'] = {'SampleType': items[x]['url'] + "/edit"}

        return items
