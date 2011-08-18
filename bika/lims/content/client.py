"""Client - the main organisational entity in bika.

$Id: Client.py 2298 2010-05-19 09:18:43Z anneline $
"""
from bika.lims import interfaces
from zope.component import getUtility
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.content.organisation import Organisation
from bika.lims.config import *
from bika.lims.interfaces import IClient
from bika.lims.utils import generateUniqueId
from zope.interface import implements
from zope.interface.declarations import alsoProvides
import sys
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('bika')

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

class Client(Organisation, HistoryAwareMixin):
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

    security.declarePublic('generateUniqueId')
    def generateUniqueId (self, type_name, batch_size = None):
        return generateUniqueId(self, type_name, batch_size)

    security.declarePublic('generateARUniqueId')
    def generateARUniqueId (self, type_name, sample_id, ar_number):
        """Generate a unique ID for new ARs
            Analysisrequests are numbered as subnumbers of the associated sample,
        """
        # get prefix
        prefixes = self.bika_setup.getPrefixes()
        type_name = type_name.replace(' ', '')
        for d in prefixes:
            if type_name == d['portal_type']:
                padding = int(d['padding'])
                prefix = d['prefix']
                break

        sample_number = sample_id.split('-')[1]
        ar_id = prefix + sample_number + '-' + str(ar_number).zfill(padding)

        return ar_id

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

    security.declarePublic('getSampleTypeDisplayList')
    def getSampleTypeDisplayList(self):
        """ return all sample types """
        sampletypes = []
        for st in self.portal_catalog(portal_type = 'SampleType',
                                      sort_on = 'sortable_title'):
            sampletypes.append((st.UID, st.Title))
        return DisplayList(sampletypes)

## gets all addable types for self ???
##        portal_types = getToolByName(self, 'portal_types')
##        myType = portal_types.getTypeInfo(self)
##        result = portal_types.listTypeInfo()
##        if myType is not None:
##            result = [t for t in result if myType.allowType(t.getId()) and
##                    t.isConstructionAllowed(self)]
##        else:
##            result = [t for t in result if t.isConstructionAllowed(self)]
##
##        return allowed_content_types and [t for t in result if t.id in allowed_content_types] or result

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(Client, PROJECTNAME)
