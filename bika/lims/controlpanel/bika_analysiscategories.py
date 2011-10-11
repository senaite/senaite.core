from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IAnalysisCategories
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from plone.app.folder.folder import ATFolderSchema, ATFolder
from zope.interface.declarations import implements
from zope.interface import alsoProvides

class AnalysisCategoriesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AnalysisCategoriesView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisCategory',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Analysis Category'):
                                    "createObject?type_name=AnalysisCategory"}
        self.icon = "++resource++bika.lims.images/category_big.png"
        self.title = _("Analysis Categories")
        self.description = ""
        self.show_editable_border = False
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
            'Title': {'title': _('Category')},
            'Description': {'title': _('Description')},
            'Department': {'title': _('Department')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['Title', 'Description', 'Department']},
            {'title': _('Active'), 'id':'active',
             'contentFilter': {'inactive_state': 'active'},
             'transitions': ['deactivate'],
             'columns': ['Title', 'Description', 'Department']},
            {'title': _('Inactive'), 'id':'inactive',
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': ['activate',],
             'columns': ['Title', 'Description', 'Department']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['Department'] = obj.getDepartment().Title()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
               (items[x]['url'], items[x]['Title'])

        return items

schema = ATFolderSchema.copy()
class AnalysisCategories(ATFolder):
    implements(IAnalysisCategories)
    schema = schema
    displayContentsTab = False

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisCategories, PROJECTNAME)
