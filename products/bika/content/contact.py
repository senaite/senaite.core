"""The contact person at an organisation.

$Id: Contact.py 2242 2010-04-08 22:17:03Z campbellbasset $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.bika.Person import Person
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
    schema = schema

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
