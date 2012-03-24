from bika.lims.utils import isActive
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
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

    def __init__(self, context, request):
        super(ARProfilesView, self).__init__(context, request)
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True

        self.columns = {
            'Title': {'title': _('Profile'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
            'ProfileKey': {'title': _('Profile Key')},
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
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description',
                         'ProfileKey']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description',
                         'ProfileKey']},
        ]

    def getProfiles(self, contentFilter={}):
        istate = contentFilter.get("inactive_state", None)
        if istate == 'active':
            profiles = [p for p in self.context.objectValues("ARProfile")
                        if isActive(p)]
        elif istate == 'inactive':
            profiles = [p for p in self.context.objectValues("ARProfile")
                        if not isActive(p)]
        else:
            profiles = [p for p in self.context.objectValues("ARProfile")]
        return profiles

    def folderitems(self):
        self.contentsMethod = self.getProfiles
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['ProfileKey'] = obj.getProfileKey()
            items[x]['Title'] = obj.Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ARTemplatesView(BikaListingView):

    def __init__(self, context, request):
        super(ARTemplatesView, self).__init__(context, request)
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True

        self.columns = {
            'Title': {'title': _('Template'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
        }

        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['Title',
                         'Description']},
            {'id':'active',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title',
                         'Description']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title',
                         'Description']},
        ]

    def getTemplates(self, contentFilter={}):
        istate = contentFilter.get("inactive_state", None)
        if istate == 'active':
            templates = [p for p in self.context.objectValues("ARTemplate")
                        if isActive(p)]
        elif istate == 'inactive':
            templates = [p for p in self.context.objectValues("ARTemplate")
                        if not isActive(p)]
        else:
            templates = [p for p in self.context.objectValues("ARTemplate")]
        return templates

    def folderitems(self):
        self.contentsMethod = self.getTemplates
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

        return items

class ARProfilesAndTemplatesView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    template = ViewPageTemplateFile("arprofiles_and_templates.pt")

    def __init__(self, context, request):
        super(ARProfilesAndTemplatesView, self).__init__(context, request)
        self.context_actions = {_('Add Profile'):
                                {'url': 'createObject?type_name=ARProfile',
                                 'icon': '++resource++bika.lims.images/add.png'},
                                _('Add Template'):
                                {'url': 'createObject?type_name=ARTemplate',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.icon = "++resource++bika.lims.images/arprofile_big.png"
        self.title = _("Analysis Request Profiles")
        self.description = ""

    def __call__(self):
        self.profiles = ARProfilesView(self.context, self.request).contents_table()
        self.templates = ARTemplatesView(self.context, self.request).contents_table()
        return self.template()

schema = ATFolderSchema.copy()
class ARProfiles(ATFolder):
    implements(IARProfiles)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ARProfiles, PROJECTNAME)
