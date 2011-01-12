"""The contact person at an organisation.

$Id: Contact.py 2242 2010-04-08 22:17:03Z campbellbasset $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.BikaMembers.Person import Person
from Products.BikaMembers.references import SymmetricalReference
from Products.bika.config import ManageClients, PUBLICATION_PREFS, PROJECTNAME
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin

schema = Person.schema.copy() + Schema((
    LinesField('PublicationPreference',
        vocabulary = PUBLICATION_PREFS,
        schemata = 'Publication preference',
        widget = MultiSelectionWidget(
            label = 'Publication preference',
            label_msgid = 'label_publicationpreference',
        ),
    ),
    BooleanField('AttachmentsPermitted',
        default = False,
        schemata = 'Publication preference',
        widget = BooleanWidget(
            label = "Attachments Permitted",
            label_msgid = "label_attachments_permitted"
        ),
    ),
    ReferenceField('CCContact',
        schemata = 'Publication preference',
        vocabulary = 'getCCContactsDisplayList',
        multiValued = 1,
        allowed_types = ('Contact',),
        relationship = 'ContactContact',
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label = 'Contacts to cc',
            label_msgid = 'label_contacts_cc',
        ),
    ),
))

schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'

IdField = schema['id']
IdField.schemata = 'default'
IdField.widget.visible = False
# Don't make title required - it will be computed from the Person's
# Fullname
TitleField = schema['title']
TitleField.schemata = 'default'
TitleField.required = 0
TitleField.widget.visible = False

class Contact(VariableSchemaSupport, BrowserDefaultMixin, Person):
    security = ClassSecurityInfo()
    archetype_name = 'Contact'
    schema = schema
    allowed_content_types = ('Address',)
    content_icon = 'contact.png'
    default_view = 'base_edit'
    immediate_view = 'base_edit'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    actions = (
        # Make view action the same as edit
        {'id': 'view',
         'name': 'View',
         'action': 'string:${object_url}/base_edit',
         'permissions': (permissions.View,),
        },

        {'id': 'access',
         'name': 'Login details',
         'action': 'string:${object_url}/contact_login_details',
         'permissions': (ManageClients,),
        },
    )

    security.declareProtected(ManageClients, 'hasUser')
    def hasUser(self):
        """ check if contact has user """
        return self.portal_membership.getMemberById(
            self.getUsername()) is not None

    security.declarePublic('getCCContactsDisplayList')
    def getCCContactsDisplayList(self):
        pairs = []
        all_contacts = self.aq_parent.getContactsDisplayList().items()
        # remove myself
        for item in all_contacts:
            if item[0] != self.UID():
                pairs.append((item[0], item[1]))
        return DisplayList(pairs)

registerType(Contact, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
