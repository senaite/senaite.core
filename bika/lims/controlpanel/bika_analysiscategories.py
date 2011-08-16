from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IAnalysisCategories
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolderSchema, ATFolder
from zope.interface.declarations import implements
from zope.interface import alsoProvides
from operator import itemgetter

class AnalysisCategoriesView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisCategory', 'sort_on': 'sortable_title'}
    content_add_actions = {_('Analysis Category'): "createObject?type_name=AnalysisCategory"}
    title = _("Analysis Categories")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = True
    show_select_column = True
    pagesize = 20

    columns = {
               'Title': {'title': _('Category')},
               'Description': {'title': _('Description')},
               'Department': {'title': _('Department')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['Title', 'Description', 'Department'],
                     'buttons':[{'cssclass': 'context',
                                 'Title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj'].getObject()
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
