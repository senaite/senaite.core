from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IHaveNoByline, IAnalysisCategories
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolderSchema, ATFolder
from zope.interface.declarations import implements
from zope.interface import alsoProvides

class AnalysisCategoriesView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'AnalysisCategory'}
    content_add_buttons = {_('Analysis Category'): "createObject?type_name=AnalysisCategory"}
    title = _("Analysis Categories")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    batch = True
    pagesize = 20

    columns = {
               'title_or_id': {'title': _('Title')},
               'CategoryDescription': {'title': _('Category Description')},
               'Department': {'title': _('Department')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['title_or_id', 'CategoryDescription', 'Department'],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['CategoryDescription'] = obj.CategoryDescription()
            items[x]['Department'] = obj.getDepartment().Title()
            items[x]['links'] = {'title_or_id': items[x]['url'] + "/base_edit",
                                 'Department': obj.getDepartment().absolute_url() + "/base_edit"}
        return items

schema = ATFolderSchema.copy()
class AnalysisCategories(ATFolder):
    implements(IAnalysisCategories, IHaveNoByline)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(AnalysisCategories, PROJECTNAME)
