from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore.utils import getToolByName
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
        bsc = getToolByName(context, 'bika_setup_catalog')
        self.contentsMethod = bsc
        self.contentFilter = {'portal_type': 'ARProfile',
                              'sort_on': 'sortable_title',
                              'path': {'query':"/".join(self.context.getPhysicalPath()),
                                       'level':0}}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=ARProfile',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.icon = "++resource++bika.lims.images/arprofile_big.png"
        self.title = _("Analysis Request Profiles")
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True

        self.columns = {
            'Title': {'title': _('Profile'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'ProfileKey': {'title': _('Profile Key'),
                           'index': 'getProfileKey',
                           'toggle': True},
        }

        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['Title',
                         'Description',
                         'ProfileKey']},
            {'id':'active',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': ['deactivate'],
             'columns': ['Title',
                         'Description',
                         'ProfileKey']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': ['activate',],
             'columns': ['Title',
                         'Description',
                         'ProfileKey']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['ProfileKey'] = obj.getProfileKey()
            items[x]['Title'] = ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

schema = ATFolderSchema.copy()
class ARProfiles(ATFolder):
    implements(IARProfiles)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ARProfiles, PROJECTNAME)
