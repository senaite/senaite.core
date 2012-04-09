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

class ProfilesAndTemplatesView(BikaListingView):

    template = ViewPageTemplateFile("profiles_and_templates.pt")

    def __init__(self, context, request):
        super(ProfilesAndTemplatesView, self).__init__(context, request)
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.table_only = True
        self.icon = "++resource++bika.lims.images/arprofile_big.png"
        self.title = _("Profiles and Templates")
        self.context_actions = {_('Add Profile'):
                                {'url': 'createObject?type_name=ARProfile',
                                 'icon': '++resource++bika.lims.images/add.png'},
                                _('Add Template'):
                                {'url': 'createObject?type_name=ARTemplate',
                                 'icon': '++resource++bika.lims.images/add.png'}}

        self.columns = {
            'Title': {'title': _('Profile'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
            'ProfileKey': {'title': _('Profile Key')},
        }

        self.review_states = [
            {'id':'ARProfiles',
             'title': _('AR Profiles'),
             'columns': ['Title',
                         'Description',
                         'ProfileKey']},
            {'id':'ARTemplates',
             'title': _('AR Templates'),
             'columns': ['Title',
                         'Description']},
            {'id':'WSTemplates',
             'title': _('WS Templates'),
             'columns': ['Title',
                         'Description']},
        ]

    def getARProfiles(self, contentFilter={}):
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

    def getARTemplates(self, contentFilter={}):
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

    def getWSTemplates(self, contentFilter={}):
        istate = contentFilter.get("inactive_state", None)
        if istate == 'active':
            templates = [p for p in self.context.bika_setup.objectValues("WSTemplate")
                        if isActive(p)]
        elif istate == 'inactive':
            templates = [p for p in self.context.objectValues("WorksheetTemplate")
                        if not isActive(p)]
        else:
            templates = [p for p in self.context.objectValues("WorksheetTemplate")]
        return templates

    def folderitems(self):
        if self.review_state == 'ARProfiles':
            self.contentsMethod = self.getARProfiles
        elif self.review_state == 'ARTemplates':
            self.contentsMethod = self.getARTemplates
        elif self.review_state == 'WSTemplates':
            self.contentsMethod = self.getWSTemplates
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])

            if self.review_state == 'ARProfiles':
                items[x]['ProfileKey'] = obj.getProfileKey()

        return items

schema = ATFolderSchema.copy()
class ARProfiles(ATFolder):
    implements(IARProfiles)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ARProfiles, PROJECTNAME)
