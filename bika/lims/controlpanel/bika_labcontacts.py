from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore import permissions
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.content.labcontact import LabContact
from plone.app.content.browser.interfaces import IFolderContentsView
from bika.lims.interfaces import ILabContacts
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class LabContactsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabContact'}
    content_add_actions = {_('Lab Contact'): "createObject?type_name=LabContact"}
    title = _("Lab Contacts")
    description = ""
    show_editable_border = False
    show_filters = False
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    pagesize = 20

    columns = {
               'getFullname': {'title': _('Full Name')},
               'Department': {'title': _('Department')},
               'BusinessPhone': {'title': _('Phone')},
               'Fax': {'title': _('Fax')},
               'MobilePhone': {'title': _('Mobile Phone')},
               'EmailAddress': {'title': _('Email Address')},
              }
    review_states = [
                    {'title': _('All'), 'id':'all',
                     'columns': ['getFullname', 'Department', 'BusinessPhone', 'Fax', 'MobilePhone', 'EmailAddress'],
                     'buttons':[{'cssclass': 'context',
                                 'title': _('Delete'),
                                 'url': 'folder_delete:method'}]},
                    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj'].getObject()
            items[x]['Department'] = obj.Department
            items[x]['BusinessPhone'] = obj.BusinessPhone
            items[x]['Fax'] = obj.BusinessFax
            items[x]['MobilePhone'] = obj.MobilePhone
            items[x]['EmailAddress'] = obj.EmailAddress
            items[x]['replace']['getFullname'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getFullname'])

        return items

schema = ATFolderSchema.copy()
class LabContacts(ATFolder):
    implements(ILabContacts)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabContacts, PROJECTNAME)
