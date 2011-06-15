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
from bika.lims.interfaces import IHaveNoByline, ILabContacts
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

class LabContactsView(BikaListingView):
    implements(IFolderContentsView)
    contentFilter = {'portal_type': 'LabContact'}
    content_add_buttons = {_('Lab Contact'): "createObject?type_name=LabContact"}
    title = _("Lab Contacts")
    description = ""
    show_editable_border = False
    batch = True
    b_size = 100
    full_objects = False
    show_editable_border = False

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
            if not items[x].has_key('brain'): continue
            obj = items[x]['brain'].getObject()
            items[x]['Department'] = obj.Department
            items[x]['BusinessPhone'] = obj.BusinessPhone
            items[x]['Fax'] = obj.BusinessFax
            items[x]['MobilePhone'] = obj.MobilePhone
            items[x]['EmailAddress'] = obj.EmailAddress
            items[x]['links'] = {'getFullname': items[x]['url'] + "/edit"}

        return items

schema = ATFolderSchema.copy()
class LabContacts(ATFolder):
    implements(ILabContacts, IHaveNoByline)
    schema = schema
    displayContentsTab = False
schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)
atapi.registerType(LabContacts, PROJECTNAME)
