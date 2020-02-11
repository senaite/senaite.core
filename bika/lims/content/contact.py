# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import types

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api import is_active
from bika.lims.config import PROJECTNAME
from bika.lims.content.person import Person
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IContact
from bika.lims.interfaces import IDeactivable
from plone import api
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements

ACTIVE_STATES = ["active"]


schema = Person.schema.copy() + atapi.Schema((
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


class Contact(Person):
    """A Contact of a Client which can be linked to a System User
    """
    implements(IContact, IDeactivable)

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
        return is_active(self)

    @security.protected(ModifyPortalContent)
    def getUser(self):
        """Returns the linked Plone User or None
        """
        username = self.getUsername()
        if not username:
            return None
        user = api.user.get(userid=username)
        return user

    @security.protected(ModifyPortalContent)
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

    @security.protected(ModifyPortalContent)
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

    @security.protected(ModifyPortalContent)
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
            if is_active(contact) and contact.UID() != self.UID():
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

    @security.private
    def _linkUser(self, user):
        """Set the UID of the current Contact in the User properties and update
        all relevant own properties.
        """
        KEY = "linked_contact_uid"

        username = user.getId()
        contact = self.getContactByUsername(username)

        # User is linked to another contact (fix in UI)
        if contact and contact.UID() != self.UID():
            raise ValueError("User '{}' is already linked to Contact '{}'"
                             .format(username, contact.Title()))

        # User is linked to multiple other contacts (fix in Data)
        if isinstance(contact, list):
            raise ValueError("User '{}' is linked to multiple Contacts: '{}'"
                             .format(username, ",".join(
                                 map(lambda x: x.Title(), contact))))

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

        # somehow the `getUsername` index gets out of sync
        self.reindexObject()

        # N.B. Local owner role and client group applies only to client
        #      contacts, but not lab contacts.
        if IClient.providedBy(self.aq_parent):
            # Grant local Owner role
            self._addLocalOwnerRole(username)
            # Add user to "Clients" group
            self._addUserToGroup(username, group="Clients")

        return True

    @security.private
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
        logger.info("Unlinked Contact UID from User {}"
                    .format(user.getProperty(KEY, "")))

        # Unset the Username
        self.setUsername(None)

        # Unset the Email
        self.setEmailAddress(None)

        # somehow the `getUsername` index gets out of sync
        self.reindexObject()

        # N.B. Local owner role and client group applies only to client
        #      contacts, but not lab contacts.
        if IClient.providedBy(self.aq_parent):
            # Revoke local Owner role
            self._delLocalOwnerRole(username)
            # Remove user from "Clients" group
            self._delUserFromGroup(username, group="Clients")

        return True

    @security.private
    def _addUserToGroup(self, username, group="Clients"):
        """Add user to the goup
        """
        portal_groups = api.portal.get_tool("portal_groups")
        group = portal_groups.getGroupById(group)
        group.addMember(username)

    @security.private
    def _delUserFromGroup(self, username, group="Clients"):
        """Remove user from the group
        """
        portal_groups = api.portal.get_tool("portal_groups")
        group = portal_groups.getGroupById(group)
        group.removeMember(username)

    @security.private
    def _addLocalOwnerRole(self, username):
        """Add local owner role from parent object
        """
        parent = self.getParent()
        if parent.portal_type == "Client":
            parent.manage_setLocalRoles(username, ["Owner", ])
            # reindex object security
            self._recursive_reindex_object_security(parent)

    @security.private
    def _delLocalOwnerRole(self, username):
        """Remove local owner role from parent object
        """
        parent = self.getParent()
        if parent.portal_type == "Client":
            parent.manage_delLocalRoles([username])
            # reindex object security
            self._recursive_reindex_object_security(parent)

    def _recursive_reindex_object_security(self, obj):
        """Reindex object security after user linking
        """
        if hasattr(aq_base(obj), "objectValues"):
            for child_obj in obj.objectValues():
                self._recursive_reindex_object_security(child_obj)

        logger.debug("Reindexing object security for {}".format(repr(obj)))
        obj.reindexObjectSecurity()


atapi.registerType(Contact, PROJECTNAME)
