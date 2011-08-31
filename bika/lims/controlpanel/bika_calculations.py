from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import ICalculations
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from operator import itemgetter

class CalculationsView(BikaListingView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(CalculationsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Calculation',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Calculation'):
                                    "createObject?type_name=Calculation"}
        self.title = _("Calculations")
        self.description = ""
        self.show_editable_border = False
        self.show_filters = False
        self.show_sort_column = False
        self.show_select_row = True
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
                   'Title': {'title': _('Calculation')},
                   'Description': {'title': _('Description')},
                   'Formula': {'title': _('Formula')},
                  }
        self.review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['Title', 'Description', 'Formula']}
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
            items[x]['Description'] = obj.Description()
            items[x]['Formula'] = obj.getFormula()

        return items

schema = ATFolderSchema.copy()
class Calculations(ATFolder):
    implements(ICalculations)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Calculations, PROJECTNAME)
