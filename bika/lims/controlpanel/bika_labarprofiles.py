from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import ILabARProfiles
from zope.interface.declarations import implements

class LabARProfilesView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabARProfile'}
    content_add_actions = {_('Lab AR Profile'): "createObject?type_name=LabARProfile"}
    title = _("Analysis Request Templates")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
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
