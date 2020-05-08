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
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import AddressField
from bika.lims.browser.widgets import AddressWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import ComputedField
from Products.Archetypes.public import ComputedWidget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import registerType
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.utils import getToolByName


schema = BikaSchema.copy() + Schema((

    StringField(
        "Salutation",
        widget=StringWidget(
            label=_("Salutation"),
            description=_("Greeting title eg. Mr, Mrs, Dr"),
        ),
    ),

    StringField(
        "Firstname",
        required=1,
        widget=StringWidget(
            label=_("Firstname"),
        ),
    ),

    StringField(
        "Middleinitial",
        required=0,
        widget=StringWidget(
            label=_("Middle initial"),
        ),
    ),

    StringField(
        "Middlename",
        required=0,
        widget=StringWidget(
            label=_("Middle name"),
        ),
    ),

    StringField(
        "Surname",
        required=1,
        widget=StringWidget(
            label=_("Surname"),
        ),
    ),

    ComputedField(
        "Fullname",
        expression="context.getFullname()",
        searchable=1,
        widget=ComputedWidget(
            label=_("Full Name"),
            visible={"edit": "invisible", "view": "invisible"},
        ),
    ),

    StringField(
        "Username",
        widget=StringWidget(
            visible=False
        ),
    ),

    StringField(
        "EmailAddress",
        schemata="Email Telephone Fax",
        searchable=1,
        widget=StringWidget(
            label=_("Email Address"),
        ),
        validators=("isEmail", )
    ),

    StringField(
        "BusinessPhone",
        schemata="Email Telephone Fax",
        widget=StringWidget(
            label=_("Phone (business)"),
        ),
    ),

    StringField(
        "BusinessFax",
        schemata="Email Telephone Fax",
        widget=StringWidget(
            label=_("Fax (business)"),
        ),
    ),

    StringField(
        "HomePhone",
        schemata="Email Telephone Fax",
        widget=StringWidget(
            label=_("Phone (home)"),
        ),
    ),

    StringField(
        "MobilePhone",
        schemata="Email Telephone Fax",
        widget=StringWidget(
            label=_("Phone (mobile)"),
        ),
    ),

    StringField(
        "JobTitle",
        widget=StringWidget(
            label=_("Job title"),
        ),
    ),

    StringField(
        "Department",
        widget=StringWidget(
            label=_("Department"),
        ),
    ),

    AddressField(
        "PhysicalAddress",
        schemata="Address",
        widget=AddressWidget(
           label=_("Physical address"),
        ),
    ),

    ComputedField(
        "City",
        expression="context.getPhysicalAddress().get('city')",
        searchable=1,
        widget=ComputedWidget(
            visible=False
        ),
    ),

    ComputedField(
        "District",
        expression="context.getPhysicalAddress().get('district')",
        searchable=1,
        widget=ComputedWidget(
            visible=False
        ),
    ),

    ComputedField(
        "PostalCode",
        expression="context.getPhysicalAddress().get('postalCode')",
        searchable=1,
        widget=ComputedWidget(
            visible=False
        ),
    ),

    ComputedField(
        "Country",
        expression="context.getPhysicalAddress().get('country')",
        searchable=1,
        widget=ComputedWidget(
            visible=False
        ),
    ),

    AddressField(
        "PostalAddress",
        schemata="Address",
        widget=AddressWidget(
           label=_("Postal address"),
        ),
    ),

))


class Person(BaseFolder):
    """Person base class
    """

    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    def getPossibleAddresses(self):
        return ["PhysicalAddress", "PostalAddress"]

    def getFullname(self):
        """Person's Fullname
        """

        fn = self.getFirstname()
        mi = self.getMiddleinitial()
        md = self.getMiddlename()
        sn = self.getSurname()
        fullname = ""
        if fn or sn:
            if mi and md:
                fullname = "%s %s %s %s" % (
                    self.getFirstname(),
                    self.getMiddleinitial(),
                    self.getMiddlename(),
                    self.getSurname())
            elif mi:
                fullname = "%s %s %s" % (
                    self.getFirstname(),
                    self.getMiddleinitial(),
                    self.getSurname())
            elif md:
                fullname = "%s %s %s" % (
                    self.getFirstname(),
                    self.getMiddlename(),
                    self.getSurname())
            else:
                fullname = '%s %s' % (self.getFirstname(), self.getSurname())
        return fullname.strip()

    Title = getFullname

    @security.protected(CMFCorePermissions.ManagePortal)
    def hasUser(self):
        """check if contact has user
        """
        return self.portal_membership.getMemberById(
            self.getUsername()) is not None


registerType(Person, PROJECTNAME)
