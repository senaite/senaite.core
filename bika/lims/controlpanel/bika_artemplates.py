from bika.lims.utils import isActive
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
from bika.lims.interfaces import IARTemplates
from zope.interface.declarations import implements

class TemplatesView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    def __init__(self, context, request):
        super(TemplatesView, self).__init__(context, request)
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.icon = "++resource++bika.lims.images/artemplate_big.png"
        self.title = _("AR Templates")
        self.description = ""
        self.context_actions = {_('Add Template'):
                                {'url': 'createObject?type_name=ARTemplate',
                                 'icon': '++resource++bika.lims.images/add.png'}}

        self.columns = {
            'Title': {'title': _('Template'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description'},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_review_state':'active'},
             'columns': ['Title',
                         'Description']},
            {'id':'inactive',
             'title': _('Inactive'),
             'contentFilter': {'inactive_review_state':'inactive'},
             'columns': ['Title',
                         'Description']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title',
                         'Description']},
        ]

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
        templates.sort(lambda a,b:cmp(a.Title().lower(), b.Title().lower()))
        return templates

    def folderitems(self):
        self.contentsMethod = self.getARTemplates
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['title'])
        return items

schema = ATFolderSchema.copy()
class ARTemplates(ATFolder):
    implements(IARTemplates)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ARTemplates, PROJECTNAME)
