# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""The contact person at an organisation.
"""
import types

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.utils import DisplayList

from plone import api
from zope.interface import implements

from bika.lims.utils import isActive
from bika.lims.interfaces import IContact
from bika.lims.content.person import Person
from bika.lims.config import PROJECTNAME
from bika.lims.config import ManageClients
from bika.lims import logger
from bika.lims import bikaMessageFactory as _

ACTIVE_STATES = ["active"]


schema = Person.schema.copy() + atapi.Schema((
    atapi.LinesField('PublicationPreference',
                     vocabulary_factory='bika.lims.vocabularies.CustomPubPrefVocabularyFactory',
                     schemata='Publication preference',
                     widget=atapi.MultiSelectionWidget(
                         label=_("Publication preference"),
                     )),
    atapi.BooleanField('AttachmentsPermitted',
                       default=False,
                       schemata='Publication preference',
                       widget=atapi.BooleanWidget(
                           label=_("Results attachments permitted"),
                           description=_(
                               "File attachments to results, e.g. microscope "
                               "photos, will be included in emails to recipients "
                               "if this option is enabled")
                       )),
    atapi.ReferenceField('CCContact',
                         schemata='Publication preference',
                         vocabulary='getContacts',
                         multiValued=1,
                         allowed_types=('Contact',),
                         relationship='ContactContact',
                         widget=atapi.ReferenceWidget(
                             checkbox_bound=0,
                             label=_("Contacts to CC"),
                         )),
))


schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'
# Don't make title required - it will be computed from the Person's Fullname
schema['title'].required = 0
schema['title'].widget.visible = False
schema.moveField('CCContact', before='AttachmentsPermitted')


class Contact(Person):
    """A Contact of a Client which can be linked to a System User
    """
    implements(IContact)

    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()
    _at_rename_after_creation = True

    @classmethod
    def getContactByUsername(cls, username):
        """Convenience Classmethod which returns a Contact by a Username
        """

        # Check if the User is linked already
        pc = api.portal.get_tool("portal_catalog")
        contacts = pc(portal_type=cls.portal_type,
                      getUsername=username)

        # No Contact assigned to this username
        if len(contacts) == 0:
            return None

        # Multiple Users assigned, this should never happen
        if len(contacts) > 1:
            logger.error("User '{}' is bound to multiple Contacts '{}'".format(
                username, ",".join(map(lambda c: c.Title, contacts))))
            return map(lambda x: x.getObject(), contacts)

        # Return the found Contact object
        return contacts[0].getObject()

    def Title(self):
        """Return the contact's Fullname as title
        """
        return safe_unicode(self.getFullname()).encode('utf-8')

    def isActive(self):
        """Checks if the Contact is active
        """
        wftool = getToolByName(self, "portal_workflow")
        status = wftool.getStatusOf("bika_inactive_workflow", self)
        if status and status.get("inactive_state") in ACTIVE_STATES:
            logger.debug("Contact '{}' is active".format(self.Title()))
            return True
        logger.debug("Contact '{}' is deactivated".format(self.Title()))
        return False

    security.declareProtected(ManageClients, 'getUser')
    def getUser(self):
        """Returns the linked Plone User or None
        """
        username = self.getUsername()
        if not username:
            return None
        user = api.user.get(userid=username)
        return user

    security.declareProtected(ManageClients, 'setUser')
    def setUser(self, user_or_username):
        """Link the user to the Contact

        :returns: True if OK, False if the User could not be linked
        :rtype: bool
        """
        user = None
        userid = None

        # Handle User IDs (strings)
        if isinstance(user_or_username, types.StringTypes):
            userid = user_or_username
            user = api.user.get(userid)
        # Handle User Objects (MemberData/PloneUser)
        if hasattr(user_or_username, "getId"):
            userid = user_or_username.getId()
            user = user_or_username

        # Not a valid user
        if user is None:
            return False

        # Link the User
        return self._linkUser(user)

    security.declareProtected(ManageClients, 'unlinkUser')
    def unlinkUser(self, delete=False):
        """Unlink the user to the Contact

        :returns: True if OK, False if no User was unlinked
        :rtype: bool
        """
        userid = self.getUsername()
        user = self.getUser()
        if user:
            logger.debug("Unlinking User '{}' from Contact '{}'".format(
                userid, self.Title()))

            # Unlink the User
            if not self._unlinkUser():
                return False

            # Also remove the Plone User (caution)
            if delete:
                logger.debug("Removing Plone User '{}'".format(userid))
                api.user.delete(username=userid)

            return True
        return False

    security.declareProtected(ManageClients, 'hasUser')
    def hasUser(self):
        """Check if Contact has a linked a System User
        """
        user = self.getUser()
        if user is None:
            return False
        return True

    def getContacts(self, dl=True):
        pairs = []
        objects = []
        for contact in self.aq_parent.objectValues('Contact'):
            if isActive(contact) and contact.UID() != self.UID():
                pairs.append((contact.UID(), contact.Title()))
                if not dl:
                    objects.append(contact)
        pairs.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return dl and DisplayList(pairs) or objects

    def getParentUID(self):
        return self.aq_parent.UID()

    def getParent(self):
        return aq_parent(aq_inner(self))

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePrivate('_linkUser')
    def _linkUser(self, user):
        """Set the UID of the current Contact in the User properties and update
        all relevant own properties.
        """
        KEY = "linked_contact_uid"

        username = user.getId()
        contact = self.getContactByUsername(username)

        # User is linked to another contact (fix in UI)
        if contact and contact.UID() != self.UID():
            raise ValueError("User '{}' is already linked to Contact '{}'".format(
                username, contact.Title()))

        # User is linked to multiple other contacts (fix in Data)
        if isinstance(contact, list):
            raise ValueError("User '{}' is linked to multiple Contacts: '{}'".format(
                username, ",".join(map(lambda x: x.Title(), contact))))

        # XXX: Does it make sense to "remember" the UID as a User property?
        tool = user.getTool()
        try:
            user.getProperty(KEY)
        except ValueError:
            logger.info("Adding User property {}".format(KEY))
            tool.manage_addProperty(KEY, "", "string")

        # Set the UID as a User Property
        uid = self.UID()
        user.setMemberProperties({KEY: uid})
        logger.info("Linked Contact UID {} to User {}".format(
            user.getProperty(KEY), username))

        # Set the Username
        self.setUsername(user.getId())

        # Update the Email address from the user
        self.setEmailAddress(user.getProperty("email"))

        # Grant local Owner role
        self._addLocalOwnerRole(username)

        # Add user to "Clients" group
        self._addUserToGroup(username, group="Clients")

        # somehow the `getUsername` index gets out of sync
        self.reindexObject()

        return True

    security.declarePrivate('_unlinkUser')
    def _unlinkUser(self):
        """Remove the UID of the current Contact in the User properties and
        update all relevant own properties.
        """
        KEY = "linked_contact_uid"

        # Nothing to do if no user is linked
        if not self.hasUser():
            return False

        user = self.getUser()
        username = user.getId()

        # Unset the UID from the User Property
        user.setMemberProperties({KEY: ""})
        logger.info("Unlinked Contact UID from User {}".format(user.getProperty(KEY, "")))

        # Unset the Username
        self.setUsername(None)

        # Unset the Email
        self.setEmailAddress(None)

        # Revoke local Owner role
        self._delLocalOwnerRole(username)

        # Remove user from "Clients" group
        self._delUserFromGroup(username, group="Clients")

        # somehow the `getUsername` index gets out of sync
        self.reindexObject()

        return True

    security.declarePrivate('_addUserToGroup')
    def _addUserToGroup(self, username, group="Clients"):
        """Add user to the goup
        """
        portal_groups = api.portal.get_tool("portal_groups")
        group = portal_groups.getGroupById('Clients')
        group.addMember(username)

    security.declarePrivate('_delUserFromGroup')
    def _delUserFromGroup(self, username, group="Clients"):
        """Remove user from the group
        """
        portal_groups = api.portal.get_tool("portal_groups")
        group = portal_groups.getGroupById(group)
        group.removeMember(username)

    security.declarePrivate('_addLocalOwnerRole')
    def _addLocalOwnerRole(self, username):
        """Add local owner role from parent object
        """
        parent = self.getParent()
        if parent.portal_type == 'Client':
            parent.manage_setLocalRoles(username, ['Owner', ])
            if hasattr(parent, 'reindexObjectSecurity'):
                parent.reindexObjectSecurity()

    security.declarePrivate('_delLocalOwnerRole')
    def _delLocalOwnerRole(self, username):
        """Remove local owner role from parent object
        """
        parent = self.getParent()
        if parent.portal_type == 'Client':
            parent.manage_delLocalRoles([ username ])
            if hasattr(parent, 'reindexObjectSecurity'):
                parent.reindexObjectSecurity()

atapi.registerType(Contact, PROJECTNAME)
