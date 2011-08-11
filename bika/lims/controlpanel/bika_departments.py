from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IDepartments
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements
from operator import itemgetter

class DepartmentsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'Department', 'sort_on': 'sortable_title'}
    content_add_actions = {_('Department'): "createObject?type_name=Department"}
    title = _("Lab Departments")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 20

    columns = {
               'Title': {'title': _('Department')},
               'Description': {'title': _('Description')},
               'Manager': {'title': _('Manager')},
               'ManagerPhone': {'title': _('Manager Phone')},
               'ManagerEmail': {'title': _('Manager Email')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['Title', 'Description', 'Manager', 'ManagerPhone', 'ManagerEmail'],
                     'buttons':[{'cssclass': 'context',
                                 'Title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
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
