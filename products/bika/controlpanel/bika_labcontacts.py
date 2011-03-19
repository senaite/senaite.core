from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.config import PROJECTNAME
from Products.bika.content.bikaschema import BikaFolderSchema
from Products.bika.content.labcontact import LabContact
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import ILabContacts
from zope.interface.declarations import implements

class LabContactsView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabContact'}
    content_add_buttons = {'Lab Contact': "createObject?type_name=LabContact"}
    title = "Lab Contacts"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
    show_editable_border = False

    columns = {
               'getFullname': {'title': 'Full Name'},
               'Department': {'title': 'Department'},
               'BusinessPhone': {'title': 'Phone'},
               'Fax': {'title': 'Fax'},
               'MobilePhone': {'title': 'Mobile Phone'},
               'EmailAddress': {'title': 'Email Address'},
              }
    wflist_states = [
                    {'title': 'All', 'id':'all',
                     'columns': ['getFullname', 'Department', 'BusinessPhone', 'Fax', 'MobilePhone', 'EmailAddress'],
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
            items[x]['links'] = {'getFullname': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class LabContacts(ATFolder):
    implements(ILabContacts)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabContacts, PROJECTNAME)
