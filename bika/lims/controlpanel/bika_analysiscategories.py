from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from Products.CMFCore.utils import getToolByName
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
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'AnalysisCategory',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=AnalysisCategory',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.icon = self.portal_url + "/++resource++bika.lims.images/category_big.png"
        self.title = self.context.translate(_("Analysis Categories"))
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Title': {'title': _('Category'),
                      'index': 'sortable_title'},
            'Description': {'title': _('Description'),
                            'index': 'description',
                            'toggle': True},
            'Department': {'title': _('Department'),
                           'index': 'getDepartmentTitle',
                           'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Title', 'Description', 'Department']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Title', 'Description', 'Department']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Title', 'Description', 'Department']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['Department'] = obj.getDepartment() and obj.getDepartment().Title() or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
               (items[x]['url'], items[x]['Title'])

        return items

schema = ATFolderSchema.copy()
class AnalysisCategories(ATFolder):
    implements(IAnalysisCategories)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisCategories, PROJECTNAME)
