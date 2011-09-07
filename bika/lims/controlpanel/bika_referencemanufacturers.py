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
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from bika.lims.interfaces import IReferenceManufacturers
from zope.interface.declarations import implements

class ReferenceManufacturersView(BikaListingView):
    implements(IFolderContentsView)
    def __init__(self, context, request):
        super(ReferenceManufacturersView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ReferenceManufacturer', 'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Reference Manufacturer'): "createObject?type_name=ReferenceManufacturer"}
        self.title = _("Reference Manufacturers")
        self.description = ""
        self.show_editable_border = False
        self.show_filters = False
        self.show_sort_column = False
        self.show_select_row = True
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
            'Title': {'title': _('Title')},
            'Description': {'title': _('Description')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['Title', 'Description']},
        ]

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['Description'] = obj.Description()
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])
        return items

schema = ATFolderSchema.copy()
class ReferenceManufacturers(ATFolder):
    implements(IReferenceManufacturers)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ReferenceManufacturers, PROJECTNAME)
