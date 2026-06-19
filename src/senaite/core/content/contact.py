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
from bika.lims import logger
from bika.lims import senaiteMessageFactory as _
from bika.lims.api import get_path
from bika.lims.api import is_active
from bika.lims.api import search
from bika.lims.api import security as sec_api
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IDeactivable
from plone import api
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from Products.PluggableAuthService.interfaces.plugins import \
    IPropertiesPlugin
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.content.person import IPersonSchema
from senaite.core.content.person import Person
from senaite.core.interfaces import IContact
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope.interface import implementer

CONTACT_UID_KEY = "linked_contact_uid"
CLIENT_UID_KEY = "linked_client_uid"


MUTABLE_PROPERTIES_PLUGIN_ID = "mutable_properties"


def _set_user_property(user, key, value):
    """Persist a string property on a user's mutable property storage.

    Registers the property on portal_memberdata the first time it's
    needed, then writes the value via the ZODB mutable property
    plugin. Going through the plugin directly avoids the cache-
    staleness bug in `MemberData.setMemberProperties`: the user's
    already-attached property sheets are built with the schema as it
    was at user-creation time and silently ignore properties
    registered later in the same request (e.g. when linking a brand-
    new user to a contact also registers the property for the first
    time). The plugin's sheet, by contrast, reflects current
    portal_memberdata.propertyMap on every call.

    Prefers the named `mutable_properties` plugin so a custom PAS
    layout that puts another writable property plugin earlier in the
    interface registration order cannot intercept the write. Falls
    back to the IPropertiesPlugin walk only when that named plugin
    is absent. Raises `RuntimeError` if no plugin accepts the write
    so callers (and tests) can surface the failure instead of seeing
    a silent loss.

    :param user: PAS user object (the one returned by `getUserById`).
    :param key: property name to write.
    :param value: string value to persist (use `""` to clear).
    :raises RuntimeError: when no property plugin can persist `key`.
    """
    portal_memberdata = user._tool
    if not portal_memberdata.hasProperty(key):
        portal_memberdata.manage_addProperty(key, "", "string")
        logger.info("Registered user property {}".format(key))

    acl_users = portal_memberdata.acl_users
    plugin = acl_users.get(MUTABLE_PROPERTIES_PLUGIN_ID, None)
    if _try_write_property(plugin, user, key, value):
        return

    # Fallback: walk every IPropertiesPlugin in registration order
    # and write to the first sheet that exposes `hasProperty` /
    # `setProperty` and already knows about `key`. Some property
    # plugins return a plain dict rather than a property sheet (e.g.
    # `pas.plugins.ldap` for non-LDAP users); those get skipped.
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


class IContactSchema(IPersonSchema):
    """Contact Schema extending Person
    """

    # Publication preference
    model.fieldset(
        "publication_preference",
        label=_(
            u"label_publication_preference",
            default=u"Publication preference"
        ),
        fields=[
            "cc_contact",
        ]
    )

    directives.widget(
        "cc_contact",
        UIDReferenceWidgetFactory,
        catalog=CONTACT_CATALOG,
        query="get_widget_cccontact_query",
        columns=[
            {"name": "getFullname", "label": _("Name")},
            {"name": "getEmailAddress", "label": _("Email")},
        ],
    )
    cc_contact = UIDReferenceField(
        title=_(
            u"label_contact_cccontact",
            default=u"Contacts to CC"
        ),
        description=_(
            u"description_contact_cccontact",
            default=u"Contacts in CC for new samples"
        ),
        allowed_types=("Contact",),
        multi_valued=True,
        required=False,
    )


@implementer(IContact, IContactSchema, IDeactivable)
class Contact(Person):
    """A Contact of a Client which can be linked to a System User
    """
    # Catalogs where this type will be catalogued
    _catalogs = [CONTACT_CATALOG]

    security = ClassSecurityInfo()

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

        NOTE: This method used the contact catalog to search for Contacts by the
        index `getUsername`.
        """
        # Check if the User is linked already
        query = {"portal_type": cls.__name__, "getUsername": username}
        contacts = search(query, CONTACT_CATALOG)

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

    def isActive(self):
        """Checks if the Contact is active
        """
        return is_active(self)

    @security.protected(permissions.ModifyPortalContent)
    def getUser(self):
        """Returns the linked Plone User or None
        """
        username = self.getUsername()
        if not username:
            return None
        user = api.user.get(userid=username)
        return user

    @security.protected(permissions.ModifyPortalContent)
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

    @security.protected(permissions.ModifyPortalContent)
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

    @security.protected(permissions.ModifyPortalContent)
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

    def isGlobal(self):
        """Check if Contact is global (not under a Client)
        """
        parent = self.getParent()
        if IClient.providedBy(parent):
            return False
        return True

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

    @security.protected(permissions.View)
    def getRawCCContact(self):
        accessor = self.accessor("cc_contact", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getCCContact(self):
        accessor = self.accessor("cc_contact")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setCCContact(self, value):
        mutator = self.mutator("cc_contact")
        mutator(self, value)

    # BBB: AT schema field property
    CCContact = property(getCCContact, setCCContact)
