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
from bika.lims.interfaces import IARProfiles
from zope.interface.declarations import implements

class ARProfilesView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'ARProfile', 'sort_on': 'sortable_title'}
    content_add_actions = {_('AR Profile'): "createObject?type_name=ARProfile"}
    title = _("Analysis Request Profiles")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 20

    columns = {
               'title': {'title': _('Profile Title')},
               'getProfileKey': {'title': _('Profile Key')},
              }
    review_states = [
                     {'title': 'All', 'id':'all',
                      'columns': ['title', 'getProfileKey'],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'},
                                {'cssclass':'context',
                                 'title': 'Duplicate',
                                 'url': 'duplicate_arprofile:method',
                                 }],
                     }
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            items[x]['replace']['title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

schema = ATFolderSchema.copy()
class ARProfiles(ATFolder):
    implements(IARProfiles)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ARProfiles, PROJECTNAME)
