# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import sys

from AccessControl import ClassSecurityInfo
from bika.lims import _
from bika.lims import api
from bika.lims.config import ARIMPORT_OPTIONS
from bika.lims.config import DECIMAL_MARKS
from bika.lims.config import EMAIL_SUBJECT_OPTIONS
from bika.lims.config import PROJECTNAME
from bika.lims.content.organisation import Organisation
from bika.lims.interfaces import IClient
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import BooleanWidget
from Products.Archetypes.public import LinesField
from Products.Archetypes.public import MultiSelectionWidget
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import ReferenceWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.content import schemata
from Products.CMFPlone.utils import safe_unicode
from zope.interface import implements


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

    StringField(
        "CCEmails",
        schemata="Preferences",
        mode="rw",
        widget=StringWidget(
            label=_("CC Emails"),
            description=_(
                "Default Emails to CC all published ARs for this client"),
            visible={
                "edit": "visible",
                "view": "visible",
            },
        ),
    ),

    LinesField(
        "EmailSubject",
        schemata="Preferences",
        default=["ar", ],
        vocabulary=EMAIL_SUBJECT_OPTIONS,
        widget=MultiSelectionWidget(
            description=_("Items to be included in email subject lines"),
            label=_("Email subject line"),
        ),
    ),

    ReferenceField(
        "DefaultCategories",
        schemata="Preferences",
        required=0,
        multiValued=1,
        vocabulary="getAnalysisCategories",
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=("AnalysisCategory",),
        relationship="ClientDefaultCategories",
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Default categories"),
            description=_(
                "Always expand the selected categories in client views"),
        ),
    ),

    ReferenceField(
        "RestrictedCategories",
        schemata="Preferences",
        required=0,
        multiValued=1,
        vocabulary="getAnalysisCategories",
        validators=("restrictedcategoriesvalidator",),
        vocabulary_display_path_bound=sys.maxint,
        allowed_types=("AnalysisCategory",),
        relationship="ClientRestrictedCategories",
        widget=ReferenceWidget(
            checkbox_bound=0,
            label=_("Restrict categories"),
            description=_("Show only selected categories in client views"),
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
        name = self.schema["Name"].get(self)
        return safe_unicode(name).encode("utf-8")

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

    security.declarePublic("getARImportOptions")

    def getARImportOptions(self):
        return ARIMPORT_OPTIONS

    security.declarePublic("getAnalysisCategories")

    def getAnalysisCategories(self):
        """Return all available analysis categories
        """
        bsc = api.get_tool("bika_setup_catalog")
        cats = []
        for st in bsc(portal_type="AnalysisCategory",
                      inactive_state="active",
                      sort_on="sortable_title"):
            cats.append((st.UID, st.Title))
        return DisplayList(cats)

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


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(Client, PROJECTNAME)
