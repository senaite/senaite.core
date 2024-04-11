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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import six
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from bika.lims import _
from bika.lims import api
from bika.lims.browser.fields import EmailsField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import DECIMAL_MARKS
from bika.lims.config import PROJECTNAME
from bika.lims.content.attachment import Attachment
from bika.lims.content.organisation import Organisation
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IDeactivable
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import registerType
from Products.ATContentTypes.content import schemata
from Products.CMFCore import permissions
from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from zope.interface import implements

schema = Organisation.schema.copy() + Schema((
    StringField(
        "ClientID",
        required=1,
        searchable=True,
        validators=("uniquefieldvalidator", "standard_id_validator"),
        widget=StringWidget(
            label=_("Client ID"),
            description=_(
                "Short and unique identifier of this client. Besides fast "
                "searches by client in Samples listings, the purposes of this "
                "field depend on the laboratory needs. For instance, the "
                "Client ID can be included as part of the Sample identifier, "
                "so the lab can easily know the client a given sample belongs "
                "to by just looking to its ID.")
        ),
    ),

    BooleanField(
        "BulkDiscount",
        default=False,
        widget=BooleanWidget(
            label=_("Bulk discount applies"),
        ),
    ),

    BooleanField(
        "MemberDiscountApplies",
        default=False,
        widget=BooleanWidget(
            label=_("Member discount applies"),
        ),
    ),

    EmailsField(
        "CCEmails",
        schemata="Preferences",
        mode="rw",
        widget=StringWidget(
            label=_("CC Emails"),
            description=_(
                "Default Emails to CC all published Samples for this client"),
            visible={
                "edit": "visible",
                "view": "visible",
            },
        ),
    ),

    # XXX: no where used -> remove?
    UIDReferenceField(
        "DefaultCategories",
        schemata="Preferences",
        required=0,
        multiValued=1,
        allowed_types=("AnalysisCategory",),
        widget=ReferenceWidget(
            visible=False,
            label=_(
                "label_client_defaultcategories",
                default="Default categories"),
            description=_(
                "description_client_defaultcategories",
                default="Always expand the selected categories"),
            catalog=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
        ),
    ),

    # TODO Fix Client restricted categories are not considered in Add sample
    UIDReferenceField(
        "RestrictedCategories",
        schemata="Preferences",
        required=0,
        multiValued=1,
        validators=("restrictedcategoriesvalidator",),
        allowed_types=("AnalysisCategory",),
        widget=ReferenceWidget(
            label=_(
                "label_client_restrictcategories",
                default="Restrict categories"),
            description=_(
                "description_client_restrictcategories",
                default="Show only selected categories"),
            catalog=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
        ),
    ),

    BooleanField(
        "DefaultDecimalMark",
        schemata="Preferences",
        default=True,
        widget=BooleanWidget(
            label=_("Default decimal mark"),
            description=_(
                "The decimal mark selected in Bika Setup will be used."),
        )
    ),

    StringField(
        "DecimalMark",
        schemata="Preferences",
        vocabulary=DECIMAL_MARKS,
        default=".",
        widget=SelectionWidget(
            label=_("Custom decimal mark"),
            description=_(
                "Decimal mark to use in the reports from this Client."),
            format="select",
        )
    ),
))

schema["title"].widget.visible = False
schema["description"].widget.visible = False
schema["EmailAddress"].schemata = "default"

schema.moveField("ClientID", after="Name")


class Client(Organisation):
    implements(IClient, IDeactivable)

    security = ClassSecurityInfo()
    schema = schema
    GROUP_KEY = "_client_group_id"

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    @property
    def group_id(self):
        """Client group ID
        """
        if not hasattr(self, self.GROUP_KEY):
            setattr(self, self.GROUP_KEY, self._get_group_id())
        return getattr(self, self.GROUP_KEY)

    def _get_group_id(self):
        """Get a valid group ID
        """
        # Try first the client ID
        client_id = self.getClientID()
        if self.is_valid_group_id(client_id):
            return client_id

        # Use the context ID
        context_id = self.getId()
        if self.is_valid_group_id(context_id):
            return context_id

        # Use the ID + prefix
        prefix_id = "group_%s" % client_id or context_id
        count = 0
        while not self.is_valid_group_id(prefix_id):
            count += 1
            prefix_id = "group_%s_%s" % (count, client_id or context_id)

        return prefix_id

    def is_valid_group_id(self, group_id):
        """Check if the group ID is valid

        :param group_id: The group ID to validate
        """
        # Check for string
        if not api.is_string(group_id):
            return False

        # Check for empty string
        if not len(group_id) > 0:
            return False

        portal = api.get_portal()
        # Check if the ID is already used by a user login
        if get_member_by_login_name(portal, group_id, False):
            return False

        return True

    @security.public
    def get_group(self):
        """Returns our client group

        :returns: Client group object
        """
        portal_groups = api.get_tool("portal_groups")
        return portal_groups.getGroupById(self.group_id)

    @security.private
    def create_group(self):
        """Create a new client group

        :returns: Client group object
        """
        group = self.get_group()

        # return the existing Group immediately
        if group:
            return group

        portal_groups = api.get_tool("portal_groups")
        group_name = self.getName()

        # Create a new Client Group
        # NOTE: The global "Client" role is necessary for the client contacts
        portal_groups.addGroup(self.group_id,
                               roles=["Client"],
                               title=group_name)

        # Grant the group the "Owner" role on ourself
        # NOTE: This will grant each member of this group later immediate
        #       access to all exisiting objects with the same role.
        self.manage_setLocalRoles(self.group_id, ["Owner"])

        return self.get_group()

    @security.private
    def remove_group(self):
        """Remove the own client group

        :returns: True if the group was removed, otherwise False
        """
        group = self.get_group()
        if not group:
            return False
        portal_groups = api.get_tool("portal_groups")
        # Use the client ID for the group ID
        portal_groups.removeGroup(self.group_id)
        # also remove the group attribute
        delattr(self, self.GROUP_KEY)
        return True

    @security.private
    def add_user_to_group(self, user):
        """Add a user to the client group

        :param user: user/group object or user/group ID
        :returns: list of new group IDs
        """
        group = self.get_group()
        if not group:
            group = self.create_group()
        return api.user.add_group(group, user)

    @security.private
    def del_user_from_group(self, user):
        """Add a user to the client group

        :param user: user/group object or user/group ID
        :returns: list of new group IDs
        """
        group = self.get_group()
        if not group:
            group = self.create_group()
        return api.user.del_group(group, user)

    @security.public
    def getGroupId(self):
        """Returns the id of the Plone's client-speficic group for this client
        """
        return self.group_id

    @security.public
    def getContactFromUsername(self, username):
        for contact in self.objectValues("Contact"):
            if contact.getUsername() == username:
                return contact.UID()

    @security.public
    def getContacts(self, active=True):
        """Return an array containing the contacts from this Client
        """
        path = api.get_path(self)
        query = {
            "portal_type": "Contact",
            "path": {"query": path},
            "is_active": active,
        }
        brains = api.search(query)
        contacts = map(api.get_object, brains)
        return list(contacts)

    @security.public
    def getDecimalMark(self):
        """Return the decimal mark to be used on reports for this client

        If the client has DefaultDecimalMark selected, the Default value from
        the LIMS Setup will be returned.

        Otherwise, will return the value of DecimalMark.
        """
        if self.getDefaultDecimalMark() is False:
            return self.Schema()["DecimalMark"].get(self)
        return self.bika_setup.getDecimalMark()

    @security.public
    def getCountry(self, default=None):
        """Return the Country from the Physical or Postal Address
        """
        physical_address = self.getPhysicalAddress().get("country", default)
        postal_address = self.getPostalAddress().get("country", default)
        return physical_address or postal_address

    @security.public
    def getProvince(self, default=None):
        """Return the Province from the Physical or Postal Address
        """
        physical_address = self.getPhysicalAddress().get("state", default)
        postal_address = self.getPostalAddress().get("state", default)
        return physical_address or postal_address

    @security.public
    def getDistrict(self, default=None):
        """Return the Province from the Physical or Postal Address
        """
        physical_address = self.getPhysicalAddress().get("district", default)
        postal_address = self.getPostalAddress().get("district", default)
        return physical_address or postal_address

    # TODO Security Make Attachments live inside ARs (instead of Client)
    # Since the Attachments live inside Client, we are forced here to overcome
    # the DeleteObjects permission when objects to delete are from Attachment
    # type. And we want to keep the DeleteObjects permission at Client level
    # because is the main container for Samples!
    # For some statuses of the AnalysisRequest type (e.g. received), the
    # permission "DeleteObjects" is granted, allowing the user to remove e.g.
    # analyses. Attachments are closely bound to Analysis and Samples, so they
    # should live inside Analysis Request.
    # Then, we will be able to remove this function from here
    def manage_delObjects(self, ids=None, REQUEST=None):
        """Overrides parent function. If the ids passed in are from Attachment
        types, the function ignores the DeleteObjects permission. For the rest
        of types, it works as usual (checks the permission)
        """
        if ids is None:
            ids = []
        if isinstance(ids, six.string_types):
            ids = [ids]

        for id in ids:
            item = self._getOb(id)
            if isinstance(item, Attachment):
                # Ignore DeleteObjects permission check
                continue
            if not _checkPermission(permissions.DeleteObjects, item):
                msg = "Do not have permissions to remove this object"
                raise Unauthorized(msg)

        return PortalFolder.manage_delObjects(self, ids, REQUEST=REQUEST)


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(Client, PROJECTNAME)
