from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.content.labcontact import LabContact
from plone.app.layout.globals.interfaces import IViewView
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.lims.interfaces import ILabContacts
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class LabContactsView(BikaListingView):
    implements(IFolderContentsView, IViewView)
    def __init__(self, context, request):
        super(LabContactsView, self).__init__(context, request)
        self.catalog = 'bika_setup_catalog'
        self.contentFilter = {'portal_type': 'LabContact',
                              'sort_on': 'sortable_title'}
        self.context_actions = {_('Add'):
                                {'url': 'createObject?type_name=LabContact',
                                 'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Lab Contacts"))
        self.icon = self.portal_url + "/++resource++bika.lims.images/lab_contact_big.png"
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25

        self.columns = {
            'Fullname': {'title': _('Name'),
                         'index': 'getFullname'},
            'Department': {'title': _('Department'),
                           'index': 'getDepartmentTitle',
                           'toggle': True},
            'BusinessPhone': {'title': _('Phone'),
                              'toggle': True},
            'Fax': {'title': _('Fax'),
                    'toggle': True},
            'MobilePhone': {'title': _('Mobile Phone'),
                            'toggle': True},
            'EmailAddress': {'title': _('Email Address'),
                             'toggle': True},
        }

        self.review_states = [
            {'id':'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id':'deactivate'}, ],
             'columns': ['Fullname',
                         'Department',
                         'BusinessPhone',
                         'Fax',
                         'MobilePhone',
                         'EmailAddress']},
            {'id':'inactive',
             'title': _('Dormant'),
             'contentFilter': {'inactive_state': 'inactive'},
             'transitions': [{'id':'activate'}, ],
             'columns': ['Fullname',
                         'Department',
                         'BusinessPhone',
                         'Fax',
                         'MobilePhone',
                         'EmailAddress']},
            {'id':'all',
             'title': _('All'),
             'contentFilter':{},
             'columns': ['Fullname',
                         'Department',
                         'BusinessPhone',
                         'Fax',
                         'MobilePhone',
                         'EmailAddress']},
        ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Fullname'] = obj.getFullname()
            items[x]['Department'] = obj.getDepartmentTitle()
            items[x]['BusinessPhone'] = obj.getBusinessPhone()
            items[x]['Fax'] = obj.getBusinessFax()
            items[x]['MobilePhone'] = obj.getMobilePhone()
            items[x]['EmailAddress'] = obj.getEmailAddress()
            items[x]['replace']['Fullname'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Fullname'])

        return items

schema = ATFolderSchema.copy()
class LabContacts(ATFolder):
    implements(ILabContacts)
    displayContentsTab = False
    schema = schema

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabContacts, PROJECTNAME)
