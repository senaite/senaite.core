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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import types

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.api import get_path
from bika.lims.api import is_active
from bika.lims.api import security as sec_api
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.person import Person
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IContact
from bika.lims.interfaces import IDeactivable
from plone import api
from Products.Archetypes import atapi
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.utils import safe_unicode
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.catalog import CONTACT_CATALOG
from zope.interface import implements

CONTACT_UID_KEY = "linked_contact_uid"
CLIENT_UID_KEY = "linked_client_uid"


MUTABLE_PROPERTIES_PLUGIN_ID = "mutable_properties"


def _set_user_property(user, key, value):
    """Persist a string property on a user's mutable property storage.

    See `senaite.core.content.contact._set_user_property` for the
    rationale; this is the AT-side mirror so contacts on either base
    write through the mutable properties plugin instead of the cached
    user sheets.

    :param user: PAS user object (the one returned by `getUserById`).
    :param key: property name to write.
    :param value: string value to persist (use `""` to clear).
    :raises RuntimeError: when no property plugin can persist `key`.
    """
    from Products.PluggableAuthService.interfaces.plugins import \
        IPropertiesPlugin

    portal_memberdata = user._tool
    if not portal_memberdata.hasProperty(key):
        portal_memberdata.manage_addProperty(key, "", "string")
        logger.info("Registered user property {}".format(key))

    acl_users = portal_memberdata.acl_users
    plugin = acl_users.get(MUTABLE_PROPERTIES_PLUGIN_ID, None)
    if _try_write_property(plugin, user, key, value):
        return

    for _id, plugin in acl_users.plugins.listPlugins(IPropertiesPlugin):
        if _try_write_property(plugin, user, key, value):
            return

    raise RuntimeError(
        "No mutable properties plugin accepted '{}' for user '{}'"
        .format(key, user.getId()))


def _try_write_property(plugin, user, key, value):
    """Attempt to persist `key` via `plugin`. Returns True on success.
    """
    if plugin is None:
        return False
    sheet = plugin.getPropertiesForUser(user)
    if sheet is None:
        return False
    has = getattr(sheet, "hasProperty", None)
    setter = getattr(sheet, "setProperty", None)
    if not callable(has) or not callable(setter):
        return False
    if not has(key):
        return False
    setter(user, key, value)
    return True


schema = Person.schema.copy() + atapi.Schema((
    UIDReferenceField(
        "CCContact",
        schemata="Publication preference",
        multiValued=1,
        allowed_types=("Contact",),
        widget=ReferenceWidget(
            label=_(
                "label_contact_cccontact",
                default="Contacts to CC"),
            description=_(
                "description_contact_cccontact",
                default="Contacts in CC for new samples"),
            catalog=CONTACT_CATALOG,
            query="get_widget_cccontact_query",
            columns=[
                {"name": "getFullname", "label": _("Name")},
                {"name": "getEmailAddress", "label": _("Email")},
            ],
        )),
))


schema["JobTitle"].schemata = "default"
schema["Department"].schemata = "default"
# Don"t make title required - it will be computed from the Person"s Fullname
schema["title"].required = 0
schema["title"].widget.visible = False


class Contact(Person):
    """A Contact of a Client which can be linked to a System User
    """
    implements(IContact, IDeactivable)

    schema = schema
    security = ClassSecurityInfo()
    _at_rename_after_creation = True

    def get_widget_cccontact_query(self, **kw):
        """Return the query for the CCContact field
        """
        path = get_path(self.aq_parent)
        query = {
            "portal_type": "Contact",
            "path": {"query": path, "depth": 1},
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        }
        logger.info("get_widget_contact_query: %r" % query)
        return query

    @classmethod
    def getContactByUsername(cls, username):
        """Convenience Classmethod which returns a Contact by a Username
        """

        # Check if the User is linked already
        cat = api.portal.get_tool(CONTACT_CATALOG)
        contacts = cat(portal_type=cls.portal_type,
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

    def getParentUID(self):
        return self.aq_parent.UID()

    def getParent(self):
        return aq_parent(aq_inner(self))

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    @security.private
    def _linkUser(self, user):
        """Set the UID of the current Contact in the User properties and update
        all relevant own properties.
        """
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

        # Set the UID as a User Property — write through the mutable
        # properties plugin so it persists for users whose cached
        # property sheets predate the registration of the property.
        uid = self.UID()
        _set_user_property(user, CONTACT_UID_KEY, uid)
        logger.info("Linked Contact UID {} to User {}".format(
            user.getProperty(CONTACT_UID_KEY, ""), username))

        # Set the Username
        self.setUsername(user.getId())

        # Update the Email address from the user
        self.setEmailAddress(user.getProperty("email"))

        # set the Fullname of the User
        user.setProperties(fullname=self.Title())

        # grant the owner role
        sec_api.grant_local_roles_for(self, roles=["Owner"], user=user)

        # somehow the `getUsername` index gets out of sync
        self.reindexObject()

        # N.B. The dynamic client-role provider grants the user the
        #      Owner role on every object of this client by checking
        #      `linked_client_uid` against the client's UID.
        #      This is a property on the user, so the catalog tokens
        #      indexed on client-tree content (`client:<uid>`) do not
        #      need to be rewritten when contacts are linked.
        if IClient.providedBy(self.aq_parent):
            _set_user_property(user, CLIENT_UID_KEY, self.aq_parent.UID())

        return True

    @security.private
    def _unlinkUser(self):
        """Remove the UID of the current Contact in the User properties and
        update all relevant own properties.
        """
        # Nothing to do if no user is linked
        if not self.hasUser():
            return False

        user = self.getUser()

        # Unset the UID from the User Property
        _set_user_property(user, CONTACT_UID_KEY, "")
        logger.info("Unlinked Contact UID from User {}"
                    .format(user.getProperty(CONTACT_UID_KEY, "")))

        # Unset the Username
        self.setUsername("")

        # Unset the Email
        self.setEmailAddress("")

        # revoke the owner role
        sec_api.revoke_local_roles_for(self, roles=["Owner"], user=user)

        # somehow the `getUsername` index gets out of sync
        self.reindexObject()

        # Clear the linked client UID so the dynamic role provider no
        # longer grants access on the client tree.
        if IClient.providedBy(self.aq_parent):
            _set_user_property(user, CLIENT_UID_KEY, "")

        return True


atapi.registerType(Contact, PROJECTNAME)
