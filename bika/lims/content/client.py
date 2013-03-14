"""Client - the main organisational entity in bika.
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims import interfaces
from bika.lims.config import *
from bika.lims.content.organisation import Organisation
from bika.lims.interfaces import IClient
from bika.lims.utils import isActive
from zope.component import getUtility
from zope.interface import implements
from zope.interface.declarations import alsoProvides
import json
import sys

schema = Organisation.schema.copy() + atapi.Schema((
    atapi.StringField('ClientID',
        required = 1,
        searchable = True,
        validators = ('uniquefieldvalidator', 'standard_id_validator'),
        widget = atapi.StringWidget(
            label = _("Client ID"),
        ),
    ),
    atapi.BooleanField('BulkDiscount',
        default = False,
        write_permission = ManageClients,
        widget = atapi.BooleanWidget(
            label = _("Bulk discount applies"),
        ),
    ),
    atapi.BooleanField('MemberDiscountApplies',
        default = False,
        write_permission = ManageClients,
        widget = atapi.BooleanWidget(
            label = _("Member discount applies"),
        ),
    ),
    atapi.LinesField('EmailSubject',
        schemata = 'Preferences',
        default = ['ar', ],
        vocabulary = EMAIL_SUBJECT_OPTIONS,
        widget = atapi.MultiSelectionWidget(
            description = _('Items to be included in email subject lines'),
            label = _("Email subject line"),
        ),
    ),
    atapi.ReferenceField('DefaultCategories',
        schemata = 'Preferences',
        required = 0,
        multiValued = 1,
        vocabulary = 'getAnalysisCategories',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisCategory',),
        relationship = 'ClientDefaultCategories',
        widget = atapi.ReferenceWidget(
            checkbox_bound = 1,
            label = _("Default categories"),
            description = _("Always expand the selected categories in client views"),
        ),
    ),
    atapi.ReferenceField('RestrictedCategories',
        schemata = 'Preferences',
        required = 0,
        multiValued = 1,
        vocabulary = 'getAnalysisCategories',
        validators = ('restrictedcategoriesvalidator',),
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('AnalysisCategory',),
        relationship = 'ClientRestrictedCategories',
        widget = atapi.ReferenceWidget(
            checkbox_bound = 1,
            label = _("Restrict categories"),
            description = _("Show only selected categories in client views"),
        ),
    ),
))

schema['AccountNumber'].write_permission = ManageClients
schema['title'].widget.visible = False
schema['description'].widget.visible = False
schema['EmailAddress'].schemata = 'default'

schema.moveField('ClientID', after='Name')

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
        return safe_unicode(self.getField('Name').get(self)).encode('utf-8')

    def setTitle(self, value):
        return self.setName(value)

    security.declarePublic('getContactFromUsername')
    def getContactFromUsername(self, username):
        for contact in self.objectValues('Contact'):
            if contact.getUsername() == username:
                return contact.UID()

    security.declarePublic('getContactUIDForUser')
    def getContactUIDForUser(self):
        """ get the UID of the user associated with the authenticated user
        """
        membership_tool = getToolByName(instance, 'portal_membership')
        member = membership_tool.getAuthenticatedMember()
        username = mtool.getAuthenticatedMember().getUserName()
        r = self.portal_catalog(
            portal_type = 'Contact',
            getUsername = username
        )
        if len(r) == 1:
            return r[0].UID


    security.declarePublic('getARImportOptions')
    def getARImportOptions(self):
        return ARIMPORT_OPTIONS

    security.declarePublic('getAnalysisCategories')
    def getAnalysisCategories(self):
        """ return all available analysis categories """
        bsc = getToolByName(self, 'bika_setup_catalog')
        cats = []
        for st in bsc(portal_type = 'AnalysisCategory',
                      inactive_state = 'active',
                      sort_on = 'sortable_title'):
            cats.append((st.UID, st.Title))
        return DisplayList(cats)

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(Client, PROJECTNAME)
