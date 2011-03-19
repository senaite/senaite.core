from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.config import PROJECTNAME
from Products.bika.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import IDepartments
from zope.interface.declarations import implements

class DepartmentsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Department'}
    content_add_buttons = {'Department': "createObject?type_name=Department"}
    title = "Lab Departments"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
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

            items[x]['links'] = {'title_or_id': items[x]['url'] + "/base_edit",
                                 'ManagerEmail': items[x]['ManagerEmail'] and "mailto:%s" % (items[x]['ManagerEmail']) or ""}

        return items

schema = ATFolderSchema.copy()
class Departments(ATFolder):
    implements(IDepartments)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Departments, PROJECTNAME)
