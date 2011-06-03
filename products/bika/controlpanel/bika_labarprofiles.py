from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.bika.browser.bika_listing import BikaListingView
from Products.bika.config import PROJECTNAME
from Products.bika import bikaMessageFactory as _
from Products.bika.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from Products.bika.interfaces.controlpanel import ILabARProfiles
from zope.interface.declarations import implements

class LabARProfilesView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabARProfile'}
    content_add_buttons = {_('Lab AR Profile'): "createObject?type_name=LabARProfile"}
    title = _("Analysis Request Templates")
    description = ""
    show_editable_border = False
    show_table_only = False
    show_sort_column = False
    show_select_row = True
    show_select_column = False
    batch = True
    pagesize = 20

    columns = {
               'getProfileTitle': {'title': _('Profile Title')},
               'getProfileKey': {'title': _('Profile Key')},
              }
    review_states = [
                     {'title': 'All', 'id':'all',
                      'columns': ['getProfileTitle', 'getProfileKey'],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'},
                                {'cssclass':'context',
                                 'title': 'Duplicate',
                                 'url': 'duplicate_labarprofile:method',
                                 }],
                     }
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            items[x]['links'] = {'getProfileTitle': items[x]['url'] + "/base_edit"}

        return items

schema = ATFolderSchema.copy()
class LabARProfiles(ATFolder):
    implements(ILabARProfiles)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabARProfiles, PROJECTNAME)
