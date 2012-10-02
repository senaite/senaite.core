"""The contact person at an organisation.
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.config import ManageClients, PUBLICATION_PREFS, PROJECTNAME
from bika.lims.content.person import Person
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.interfaces import IContact
from zope.interface import implements

schema = Person.schema.copy() + Schema((
    LinesField('PublicationPreference',
        vocabulary = PUBLICATION_PREFS,
        schemata = 'Publication preference',
        widget = MultiSelectionWidget(
            label = _("Publication preference"),
        ),
    ),
    BooleanField('AttachmentsPermitted',
        default = False,
        schemata = 'Publication preference',
        widget = BooleanWidget(
            label = _("Attachments Permitted"),
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
            label = _("Contacts to CC"),
        ),
    ),
))

schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False

class Contact(Person):
    implements(IContact)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the contact's Fullname as title """
        return str(self.getFullname()).decode('utf-8').encode('utf-8')

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

atapi.registerType(Contact, PROJECTNAME)
