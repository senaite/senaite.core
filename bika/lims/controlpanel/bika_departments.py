from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IDepartments
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from operator import itemgetter

class DepartmentsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(DepartmentsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'Department',
                              'sort_on': 'sortable_title'}
        self.content_add_actions = {_('Add'):
                                    "createObject?type_name=Department"}
        self.title = _("Lab Departments")
        self.icon = "++resource++bika.lims.images/department_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 20

        self.columns = {
            'Title': {'title': _('Department'),
                      'index':'sortable_title'},
            'Description': {'title': _('Description')},
            'Manager': {'title': _('Manager')},
            'ManagerPhone': {'title': _('Manager Phone')},
            'ManagerEmail': {'title': _('Manager Email')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['Title',
                         'Description',
                         'Manager',
                         'ManagerPhone',
                         'ManagerEmail']},
            {'title': _('Active'), 'id':'active',
             'contentFilter': {'inactive_state': 'active'},
             'transitions': ['deactivate'],
             'columns': ['Title',
                         'Description',
                         'Manager',
                         'ManagerPhone',
                         'ManagerEmail']},
            {'title': _('Dormant'), 'id':'inactive',
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': ['activate',],
             'columns': ['Title',
                         'Description',
                         'Manager',
                         'ManagerPhone',
                         'ManagerEmail']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Description'] = obj.Description()
            items[x]['Manager'] = obj.getManagerName()
            if items[x]['Manager']:
                items[x]['ManagerPhone'] = obj.getManager().BusinessPhone
                items[x]['ManagerEmail'] = obj.getManager().EmailAddress
            else:
                items[x]['ManagerPhone'] = ""
                items[x]['ManagerEmail'] = ""

            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

            if items[x]['ManagerEmail']:
                items[x]['replace']['ManagerEmail'] = "<a href='%s'>%s</a>"%\
                     ('mailto:%s' % items[x]['ManagerEmail'],
                      items[x]['ManagerEmail'])


        return items

schema = ATFolderSchema.copy()
class Departments(ATFolder):
    implements(IDepartments)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(Departments, PROJECTNAME)
