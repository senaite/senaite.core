"""ReferenceSuppliers is a container for ReferenceSupplier instances.
"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from ZODB.POSException import ConflictError
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IReferenceSuppliers
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.utils import generateUniqueId
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

class ReferenceSuppliersView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    def __init__(self, context, request):
        super(ReferenceSuppliersView, self).__init__(context, request)
        self.title = _("Reference Suppliers")
        self.icon = "++resource++bika.lims.images/referencesupplier_big.png"
        self.description = _("")
        self.contentFilter = {'portal_type': 'ReferenceSupplier',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Add'): "createObject?type_name=ReferenceSupplier"}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 50

        self.request.set('disable_border', 1)

        self.columns = {
            'Name': {'title': _('Name'),
                     'index': 'getName'},
            'Email': {'title': _('Email'),
                      'index': 'getEmailAddress'},
            'Phone': {'title': _('Phone'),
                      'index': 'getPhone'},
            'Fax': {'title': _('Fax'),
                    'index': 'getFax'},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'columns': ['Name',
                         'Email',
                         'Phone',
                         'Fax']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Name'] = obj.getName()
            items[x]['Email'] = obj.getEmailAddress()
            items[x]['Phone'] = obj.getPhone()
            items[x]['Fax'] = obj.getFax()
            items[x]['replace']['Name'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Name'])

        return items

schema = ATFolderSchema.copy()
class ReferenceSuppliers(ATFolder):
    implements(IReferenceSuppliers)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(ReferenceSuppliers, PROJECTNAME)
