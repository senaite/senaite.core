"""Client - the main organisational entity in bika. 

$Id: Client.py 2298 2010-05-19 09:18:43Z anneline $
"""
import sys
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ListFolderContents, \
    ModifyPortalContent, View
from Products.CMFCore import permissions
from Products.Archetypes.public import *
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.utils import DisplayList
from Products.BikaMembers import Organisation
from Products.bika.config import ManageClients
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.config import CLIENT_TYPES, ARIMPORT_OPTIONS, EMAIL_SUBJECT_OPTIONS

schema = Organisation.schema.copy() + Schema((
        StringField('ClientID',
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Client ID',
            label_msgid = 'label_clientid',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    BooleanField('MemberDiscountApplies',
        default = False,
        schemata = 'default',
        write_permission = ManageClients,
        widget = BooleanWidget(
            label = "Member discount applies",
            label_msgid = "label_member_discount_applies",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('ClientType',
        required = 1,
        default = 'noncorporate',
        write_permission = ManageClients,
        vocabulary = CLIENT_TYPES,
        widget = SelectionWidget(
            label = 'Client type',
            label_msgid = 'label_client_type',
        ),
    ),
    LinesField('EmailSubject',
        schemata = 'preferences',
        default = ['ar', ],
        vocabulary = EMAIL_SUBJECT_OPTIONS,
        widget = MultiSelectionWidget(
            description = 'Items to be included in email subject lines',
            label = 'Email subject line',
            label_msgid = 'label_email_subject_line',
        ),
    ),
    ReferenceField('DefaultCategory',
        schemata = 'preferences',
        required = 0,
        multiValued = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisCategory',),
        relationship = 'ClientAnalysisCategory',
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Default analysis categories',
            label_msgid = 'label_default_categories',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    BooleanField('RestrictCategories',
        default = False,
        schemata = 'preferences',
        widget = BooleanWidget(
            label = "Restrict client to selected categories",
            label_msgid = "label_restrice_categories",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
))
for field_id in ('Name', 'EmailAddress', 'Phone', 'Fax'):
    schema[field_id].index = 'FieldIndex:brains'

AccountNumber = schema['AccountNumber']
AccountNumber.write_permission = ManageClients

IdField = schema['id']
IdField.widget.visible = {'edit':'hidden', 'view': 'invisible'}
TitleField = schema['title']

class Client(VariableSchemaSupport, BrowserDefaultMixin, BaseBTreeFolder,
             Organisation.Organisation):
    security = ClassSecurityInfo()
    archetype_name = 'Client'
    schema = schema
    content_icon = 'client.png'
    allowed_content_types = ('AnalysisRequest', 'Sample', 'Contact', 'Order',
                    'ARImport', 'ARProfile', 'AnalysisSpec', 'Attachment')
    immediate_view = 'base_edit'
    default_view = 'client_analysisrequests'
    use_folder_tabs = 0
    global_allow = 0
    filter_content_types = 1

    actions = (
        # Make view action the same as edit
        {'id': 'checkstate',
         'name': 'CheckState',
         'action': 'string:${object_url}/base_edit',
         'condition': 'python:here.getSetupState()',
         'permissions': (View,),
        },
        {'id': 'view',
         'name': 'View',
         'action': 'string:${object_url}/base_edit',
         'condition': 'python:here.setup_state',
         'permissions': (ModifyPortalContent,),
        },
        {'id': 'edit',
         'name': 'Edit',
         'action': 'string:${object_url}/base_edit',
         'condition': 'python:here.setup_state',
         'permissions': (ModifyPortalContent,),
        },
        {'id': 'contacts',
         'name': 'Contacts',
         'action': 'string:${object_url}/client_contacts',
         'condition': 'python:here.setup_state',
         'permissions': (ListFolderContents,),
        },
        {'id': 'samples',
         'name': 'Samples',
         'action': 'string:${object_url}/client_samples',
         'condition': 'python:not here.setup_state',
         'permissions': (ListFolderContents,),
        },
        {'id': 'requests',
         'name': 'Analysis Requests',
         'action': 'string:${object_url}/client_analysisrequests',
         'condition': 'python:not here.setup_state',
         'permissions': (ListFolderContents,),
        },
        {'id': 'attachments',
         'name': 'Attachments',
         'action': 'string:${object_url}/client_attachments',
         'condition': 'python:(not here.setup_state) and here.bika_settings.settings.getAttachmentsPermitted()',
         'permissions': (ListFolderContents,),
        },
        {'id': 'arimports',
         'name': 'imports',
         'action': 'string:${object_url}/client_arimports',
         'condition': 'python:not here.setup_state',
         'permissions': (ListFolderContents,),
        },
        {'id': 'AR_profiles',
         'name': 'profiles',
         'action': 'string:${object_url}/client_arprofiles',
         'condition': 'python:here.setup_state',
         'permissions': (ListFolderContents,),
        },
        {'id': 'analysisspecs',
         'name': 'specs',
         'action': 'string:${object_url}/client_analysisspecs',
         'condition': 'python:here.setup_state',
         'permissions': (ListFolderContents,),
        },
        {'id': 'orders',
         'name': 'Orders',
         'action': 'string:${object_url}/client_orders',
         'condition': 'python:not here.setup_state',
         'permissions': (ListFolderContents,),
        },
        {'id': 'clientsetup',
         'name': 'Setup',
         'action': 'string:${object_url}/redirect_to_client_setup',
         'condition': 'python:not here.setup_state',
         'permissions': (ListFolderContents,),
        },
        {'id': 'clientactions',
         'name': 'Actions',
         'action': 'string:${object_url}/redirect_to_client_actions',
         'condition': 'python:here.setup_state',
         'permissions': (ListFolderContents,),
        },
    )
    
    setup_state = False

    def Title(self):
        """ Return the Organisation's Name as its title """
        return self.getField('Name').get(self)

    def getSetupState(self):
        """ Return the Organisation's Name as its title """
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

registerType(Client, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
