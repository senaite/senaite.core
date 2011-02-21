"""Client - the main organisational entity in bika. 

$Id: Client.py 2298 2010-05-19 09:18:43Z anneline $
"""

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.bika.content.organisation import Organisation
from Products.bika import bikaMessageFactory as _
from Products.bika.config import *
from Products.bika.interfaces import IClient
from zope.interface import implements
from zope.interface.declarations import alsoProvides
import sys

schema = Organisation.schema.copy() + atapi.Schema((
    atapi.StringField('ClientID',
        index = 'FieldIndex:brains',
        searchable = True,
        widget = atapi.StringWidget(
            label = 'Client ID',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    atapi.BooleanField('MemberDiscountApplies',
        default = False,
        schemata = 'default',
        write_permission = ManageClients,
        widget = atapi.BooleanWidget(
            label = "Member discount applies",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    atapi.StringField('ClientType',
        required = 1,
        default = 'noncorporate',
        write_permission = ManageClients,
        vocabulary = CLIENT_TYPES,
        widget = atapi.SelectionWidget(
            label = 'Client type',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    atapi.LinesField('EmailSubject',
        schemata = 'preferences',
        default = ['ar', ],
        vocabulary = EMAIL_SUBJECT_OPTIONS,
        widget = atapi.MultiSelectionWidget(
            description = 'Items to be included in email subject lines',
            label = 'Email subject line',
            i18n_domain = I18N_DOMAIN,
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
            label = 'Default analysis categories',
            label_msgid = 'label_default_categories',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    atapi.BooleanField('RestrictCategories',
        default = False,
        schemata = 'preferences',
        widget = atapi.BooleanWidget(
            label = "Restrict client to selected categories",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))


schema['AccountNumber'].write_permission = ManageClients
schema['title'].widget.visible = False
schema['description'].widget.visible = False

class Client(BrowserDefaultMixin, Organisation):
    implements(IClient)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    setup_state = False

    def Title(self):
        """ Return the Organisation's Name as its title """
        return self.getField('Name').get(self)

    def getSetupState(self):
        """ Flag to show subtabs for client setup pages """
        if self.get_client_setup_state() == "setup":
            self.setup_state = True
        else:
            self.setup_state = False
        return False

    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        pairs = []
        for contact in self.objectValues('Contact'):
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

    security.declarePublic('getRemainingSampleTypes')
    def getRemainingSampleTypes(self, current_sampletype):
        """ return all unused sample types """
        """ plus the current one being edited """
        unavailable_sampletypes = []
        for spec in self.objectValues('AnalysisSpec'):
            st = spec.getSampleType()
            if not st.UID() == current_sampletype:
                unavailable_sampletypes.append(st.UID())

        available_sampletypes = []
        for st in self.portal_catalog(portal_type = 'SampleType',
                                      sort_on = 'sortable_title'):
            if st.UID not in unavailable_sampletypes:
                available_sampletypes.append((st.UID, st.Title))

        return DisplayList(available_sampletypes)

    security.declarePublic('getSampleTypeDisplayList')
    def getSampleTypeDisplayList(self):
        """ return all sample types """
        sampletypes = []
        for st in self.portal_catalog(portal_type = 'SampleType',
                                      sort_on = 'sortable_title'):
            sampletypes.append((st.UID, st.Title))
        return DisplayList(sampletypes)

        portal_types = getToolByName(self, 'portal_types')
        myType = portal_types.getTypeInfo(self)
        result = portal_types.listTypeInfo()
        if myType is not None:
            result = [t for t in result if myType.allowType(t.getId()) and
                    t.isConstructionAllowed(self)]
        else:
            result = [t for t in result if t.isConstructionAllowed(self)]

        return allowed_content_types and [t for t in result if t.id in allowed_content_types] or result


schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(Client, PROJECTNAME)
