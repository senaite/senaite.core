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

from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import registerType
from Products.CMFCore import permissions
from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder
from Products.CMFCore.utils import _checkPermission
from zope.interface import implements

from bika.lims import _
from bika.lims import api
from bika.lims.browser.fields import EmailsField
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import DECIMAL_MARKS
from bika.lims.config import PROJECTNAME
from bika.lims.content.attachment import Attachment
from bika.lims.content.organisation import Organisation
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IDeactivable

schema = Organisation.schema.copy() + Schema((
    StringField(
        "ClientID",
        required=1,
        searchable=True,
        validators=("uniquefieldvalidator", "standard_id_validator"),
        widget=StringWidget(
            label=_("Client ID"),
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

    ReferenceField(
        "DefaultCategories",
        schemata="Preferences",
        required=0,
        multiValued=1,
        allowed_types=("AnalysisCategory",),
        relationship="ClientDefaultCategories",
        widget=ReferenceWidget(
            label=_("Default categories"),
            description=_(
                "Always expand the selected categories in client views"),
            showOn=True,
            catalog_name=SETUP_CATALOG,
            base_query=dict(
                is_active=True,
                sort_on="sortable_title",
                sort_order="ascending",
            ),
        ),
    ),

    ReferenceField(
        "RestrictedCategories",
        schemata="Preferences",
        required=0,
        multiValued=1,
        validators=("restrictedcategoriesvalidator",),
        allowed_types=("AnalysisCategory",),
        relationship="ClientRestrictedCategories",
        widget=ReferenceWidget(
            label=_("Restrict categories"),
            description=_("Show only selected categories in client views"),
            showOn=True,
            catalog_name=SETUP_CATALOG,
            base_query=dict(
                is_active=True,
                sort_on="sortable_title",
                sort_order="ascending",
            ),
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
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic("getContactFromUsername")

    def getContactFromUsername(self, username):
        for contact in self.objectValues("Contact"):
            if contact.getUsername() == username:
                return contact.UID()

    security.declarePublic("getContactUIDForUser")

    def getContactUIDForUser(self):
        """Get the UID of the user associated with the authenticated user
        """
        membership_tool = api.get_tool("portal_membership")
        member = membership_tool.getAuthenticatedMember()
        username = member.getUserName()
        r = self.portal_catalog(
            portal_type="Contact",
            getUsername=username
        )
        if len(r) == 1:
            return r[0].UID

    def getContacts(self, only_active=True):
        """Return an array containing the contacts from this Client
        """
        contacts = self.objectValues("Contact")
        if only_active:
            contacts = filter(api.is_active, contacts)
        return contacts

    def getDecimalMark(self):
        """Return the decimal mark to be used on reports for this client

        If the client has DefaultDecimalMark selected, the Default value from
        the LIMS Setup will be returned.

        Otherwise, will return the value of DecimalMark.
        """
        if self.getDefaultDecimalMark() is False:
            return self.Schema()["DecimalMark"].get(self)
        return self.bika_setup.getDecimalMark()

    def getCountry(self, default=None):
        """Return the Country from the Physical or Postal Address
        """
        physical_address = self.getPhysicalAddress().get("country", default)
        postal_address = self.getPostalAddress().get("country", default)
        return physical_address or postal_address

    def getProvince(self, default=None):
        """Return the Province from the Physical or Postal Address
        """
        physical_address = self.getPhysicalAddress().get("state", default)
        postal_address = self.getPostalAddress().get("state", default)
        return physical_address or postal_address

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
        if isinstance(ids, basestring):
            ids = [ids]

        for id in ids:
            item = self._getOb(id)
            if isinstance(item, Attachment):
                # Ignore DeleteObjects permission check
                continue
            if not _checkPermission(permissions.DeleteObjects, item):
                raise Unauthorized, (
                    "Do not have permissions to remove this object")
        return PortalFolder.manage_delObjects(self, ids, REQUEST=REQUEST)


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(Client, PROJECTNAME)
