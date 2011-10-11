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
from plone.app.layout.globals.interfaces import IViewView
from bika.lims.interfaces import IARProfiles
from zope.interface.declarations import implements

class ARProfilesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ARProfilesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ARProfile',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('AR Profile'):
                                    "createObject?type_name=ARProfile"}
        self.icon = "++resource++bika.lims.images/arprofile_big.png"
        self.title = _("Analysis Request Profiles")
        self.description = ""
        self.show_editable_border = True
        self.show_filters = False
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
            'title': {'title': _('Profile')},
            'Description': {'title': _('Description')},
            'ProfileKey': {'title': _('Profile Key')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['title', 'Description', 'ProfileKey']},
            {'title': _('Active'), 'id':'active',
             'contentFilter': {'inactive_state': 'active'},
             'transitions': ['deactivate'],
             'columns': ['title', 'Description', 'ProfileKey']},
            {'title': _('Inactive'), 'id':'inactive',
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': ['activate',],
             'columns': ['title', 'Description', 'ProfileKey']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['ProfileKey'] = obj.getProfileKey()
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
