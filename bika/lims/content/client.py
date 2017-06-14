# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""Client - the main organisational entity in bika.
"""

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi, DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.config import ARIMPORT_OPTIONS, PROJECTNAME
from bika.lims.content.organisation import Organisation
from bika.lims.content.schema.client import schema
from bika.lims.interfaces import IClient
from bika.lims.workflow import InactiveState, StateFlow, getCurrentState
from zope.interface import implements


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
        """Return the Organisation's Name as its title
        """
        name = self.schema['Name'].get(self)
        return safe_unicode(name).encode('utf-8')

    security.declarePublic('getContactFromUsername')

    def getContactFromUsername(self, username):
        for contact in self.objectValues('Contact'):
            if contact.getUsername() == username:
                return contact.UID()

    security.declarePublic('getContactUIDForUser')

    def getContactUIDForUser(self):
        """get the UID of the user associated with the authenticated user
        """
        membership_tool = getToolByName(self, 'portal_membership')
        member = membership_tool.getAuthenticatedMember()
        username = member.getUserName()
        r = self.portal_catalog(portal_type='Contact', getUsername=username)
        if len(r) == 1:
            return r[0].UID

    security.declarePublic('getARImportOptions')

    def getARImportOptions(self):
        return ARIMPORT_OPTIONS

    security.declarePublic('getAnalysisCategories')

    def getAnalysisCategories(self):
        """return all available analysis categories """
        bsc = getToolByName(self, 'bika_setup_catalog')
        cats = []
        for st in bsc(portal_type='AnalysisCategory',
                      inactive_state='active',
                      sort_on='sortable_title'):
            cats.append((st.UID, st.Title))
        return DisplayList(cats)

    def getContacts(self, only_active=True):
        """Return an array containing the contacts from this Client
        """
        contacts = self.objectValues('Contact')
        if only_active:
            contacts = [
                c for c in contacts if
                getCurrentState(c, StateFlow.inactive) == InactiveState.active
            ]
        return contacts

    def getDecimalMark(self):
        """Return the decimal mark to be used on reports for this
            client. If the client has DefaultDecimalMark selected, the
            Default value from Bika Setup will be returned. Otherwise,
            will return the value of DecimalMark.
        """
        if not self.getDefaultDecimalMark():
            return self.getField('DecimalMark').get(self)
        return self.bika_setup.getDecimalMark()

    def getCountry(self, default=None):
        """Return the Country from the Physical or Postal Address
        """
        physical_address = self.getPhysicalAddress().get("country", default)
        postal_address = self.getPostalAddress().get("country", default)
        return physical_address if physical_address else postal_address

    def getProvince(self, default=None):
        """Return the Province from the Physical or Postal Address
        """
        physical_address = self.getPhysicalAddress().get("state", default)
        postal_address = self.getPostalAddress().get("state", default)
        return physical_address if physical_address else postal_address

    def getDistrict(self, default=None):
        """Return the Province from the Physical or Postal Address
        """
        physical_address = self.getPhysicalAddress().get("district", default)
        postal_address = self.getPostalAddress().get("district", default)
        return physical_address if physical_address else postal_address

    # noinspection PyUnusedLocal
    def validate_address(self, request, field, data):
        """Validates the Address Fields
        :returns: (str) message if validation fails, otherwise (bool) True
        """
        province = data.get("state", None)
        district = data.get("district", None)

        if not all([province, district]):
            return "Province and district fields are mandatory"

        return True


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(Client, PROJECTNAME)
