from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.bika.browser.bika_folder_contents import BikaFolderContentsView
from Products.bika.config import PROJECTNAME
from Products.bika.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import ILabARProfiles
from zope.interface.declarations import implements

class LabARProfilesView(BikaFolderContentsView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabARProfile'}
    content_add_buttons = {'Lab AR Profile': "createObject?type_name=LabARProfile"}
    title = "Analysis Request Templates"
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
    columns = {
               'getProfileTitle': {'title': 'Profile Title'},
               'getProfileKey': {'title': 'Profile Key'},
              }
    wflist_states = [
                     {'title': 'All', 'id':'all',
                      'columns': ['getProfileTitle', 'getProfileKey'],
                      'buttons':[BikaFolderContentsView.default_buttons['delete'],
                                 {'cssclass':'context',
                                  'title': 'Duplicate',
                                  'url': 'duplicate_labarprofile:method', # XXX Duplicate LabARProfile
                                 }
                                ],
                     }
                    ]

    def folderitems(self):
        items = BikaFolderContentsView.folderitems(self)
        for x in range(len(items)):
            items[x]['links'] = {'getProfileTitle': items[x]['url'] + "/base_edit"}

        return items

schema = ATFolderSchema.copy()
class LabARProfiles(ATFolder):
    implements(ILabARProfiles)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabARProfiles, PROJECTNAME)
