"""Client - the main organisational entity in bika.
"""
from bika.lims import interfaces
from zope.component import getUtility
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.content.organisation import Organisation
from bika.lims.config import *
from bika.lims.interfaces import IClient
from zope.interface import implements
from zope.interface.declarations import alsoProvides
import sys
from bika.lims import bikaMessageFactory as _

schema = Organisation.schema.copy() + atapi.Schema((
    atapi.StringField('ClientID',
        searchable = True,
        widget = atapi.StringWidget(
            label = _("Client ID"),
        ),
    ),
    atapi.BooleanField('MemberDiscountApplies',
        default = False,
        schemata = 'default',
        write_permission = ManageClients,
        widget = atapi.BooleanWidget(
            label = _("Member discount applies"),
        ),
    ),
    atapi.StringField('ClientType',
        required = 1,
        default = 'noncorporate',
        write_permission = ManageClients,
        vocabulary = CLIENT_TYPES,
        widget = atapi.SelectionWidget(
            label = _("Client Type"),
        ),
    ),
    atapi.LinesField('EmailSubject',
        schemata = 'preferences',
        default = ['ar', ],
        vocabulary = EMAIL_SUBJECT_OPTIONS,
        widget = atapi.MultiSelectionWidget(
            description = 'Items to be included in email subject lines',
            label = _("Email subject line"),
        ),
    ),
    atapi.ReferenceField('DefaultCategory',
        schemata = 'preferences',
        required = 0,
        multiValued = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisCategory',),
        relationship = 'ClientAnalysisCategory',
        widget = atapi.ReferenceWidget(
            checkbox_bound = 1,
            label = _("Default analysis categories"),
        ),
    ),
    atapi.BooleanField('RestrictCategories',
        default = False,
        schemata = 'preferences',
        widget = atapi.BooleanWidget(
            label = _("Restrict client to selected categories"),
        ),
    ),
))

schema['AccountNumber'].write_permission = ManageClients
schema['title'].widget.visible = False
schema['description'].widget.visible = False

class Client(Organisation):
    implements(IClient)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        """ Return the Organisation's Name as its title """
        return self.getField('Name').get(self)

    def setTitle(self, value):
        return self.setName(value)

    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        wf = getToolByName(self, 'portal_workflow')
        pairs = []
        for contact in self.objectValues('Contact'):
            if wf.getInfoFor(contact, 'inactive_state', '') == 'active':
                pairs.append((contact.UID(), contact.Title()))
        # sort the list by the second item
        pairs.sort(lambda x, y:cmp(x[1], y[1]))
        return DisplayList(pairs)

    security.declarePublic('getContactFromUsername')
    def getContactFromUsername(self, username):
        for contact in self.objectValues('Contact'):
            if contact.getUsername() == username:
                return contact.UID()
        return

    security.declarePublic('getCCContacts')
    def getCCContacts(self):
        # for every contact, get the list of CC Contacts
        # using comma delimited strings in arrays so that it can
        # be manipulated in javascript
        client_ccs = []
        cc_data = {}
        for contact in self.objectValues('Contact'):
            cc_contacts = []
            cc_uids = ''
            cc_titles = ''
            for cc_contact in contact.getCCContact():
                if wf.getInfoFor(cc_contact, 'inactive_state', '') == 'active':
                    if cc_uids:
                        cc_uids = cc_uids + ', ' + cc_contact.UID()
                        cc_titles = cc_titles + ', ' + cc_contact.Title()
                    else:
                        cc_uids = cc_contact.UID()
                        cc_titles = cc_contact.Title()
            cc_contacts.append(contact.UID())
            cc_contacts.append(cc_uids)
            cc_contacts.append(cc_titles)
            cc_data[contact.Title()] = cc_contacts

        cc_keys = cc_data.keys()
        cc_keys.sort()
        for cc_key in cc_keys:
            client_ccs.append(cc_data[cc_key])
        return client_ccs

    security.declarePublic('getContactUIDForUser')
    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        r = self.portal_catalog(
            portal_type = 'Contact',
            getUsername = user_id
        )
        if len(r) == 1:
            return r[0].UID

    security.declarePublic('getARImportOptions')
    def getARImportOptions(self):
        return ARIMPORT_OPTIONS

    security.declarePublic('getSampleTypeDisplayList')
    def getSampleTypeDisplayList(self):
        """ return all sample types """
        bsc = getToolByName(self, 'bika_setup_catalog')
        sampletypes = []
        for st in bsc(portal_type = 'SampleType',
                      sort_on = 'sortable_title'):
            sampletypes.append((st.UID, st.Title))
        return DisplayList(sampletypes)

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(Client, PROJECTNAME)
