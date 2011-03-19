from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.config import PROJECTNAME
from Products.bika.interfaces.controlpanel import IAnalysisCategories
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolderSchema, ATFolder
from zope.interface.declarations import implements

class AnalysisCategoriesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisCategory'}
    content_add_buttons = {'Analysis Category': "createObject?type_name=AnalysisCategory"}
    title = "Analysis Categories"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
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
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/base_edit",
                                 'Department': obj.getDepartment().absolute_url() + "/base_edit"}
        return items

schema = ATFolderSchema.copy()
class AnalysisCategories(ATFolder):
    implements(IAnalysisCategories)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisCategories, PROJECTNAME)
