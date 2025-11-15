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

from AccessControl import ClassSecurityInfo
from bika.lims import senaiteMessageFactory as _
from bika.lims.api import mail
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from Products.CMFPlone.utils import safe_unicode
from senaite.core.content.base import Container
from senaite.core.schema import AddressField
from senaite.core.schema import PhoneField
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.schema.addressfield import POSTAL_ADDRESS
from senaite.core.z3cform.widgets.address import AddressWidget
from senaite.core.z3cform.widgets.phone import PhoneWidget
from zope import schema
from zope.interface import implementer
from zope.interface import invariant
from zope.interface.exceptions import Invalid


class IPersonSchema(model.Schema):
    """Base schema for Person-based content types
    """

    # Hidden fields
    directives.omitted("title")
    directives.omitted("description")
    directives.omitted("username")

    title = schema.TextLine(
        title=_(
            u"label_person_title",
            default=u"Title"
        ),
        required=False,
    )

    description = schema.Text(
        title=_(
            "label_person_description",
            default="Description",
        ),
        required=False,
    )

    salutation = schema.TextLine(
        title=_(
            u"label_person_salutation",
            default=u"Salutation"
        ),
        description=_(
            u"description_person_salutation",
            default=u"Greeting title eg. Mr, Mrs, Dr"
        ),
        required=False,
    )

    firstname = schema.TextLine(
        title=_(
            u"label_person_firstname",
            default=u"Firstname"
        ),
        required=True,
    )

    middleinitial = schema.TextLine(
        title=_(
            u"label_person_middleinitial",
            default=u"Middle initial"
        ),
        required=False,
    )

    middlename = schema.TextLine(
        title=_(
            u"label_person_middlename",
            default=u"Middle name"
        ),
        required=False,
    )

    surname = schema.TextLine(
        title=_(
            u"label_person_surname",
            default=u"Surname"
        ),
        required=True,
    )

    job_title = schema.TextLine(
        title=_(
            u"label_person_job_title",
            default=u"Job title"
        ),
        required=False,
    )

    department = schema.TextLine(
        title=_(
            u"label_person_department",
            default=u"Department"
        ),
        required=False,
    )

    username = schema.TextLine(
        title=_(
            u"label_person_username",
            default=u"Username"
        ),
        required=False,
    )

    # Contact information
    model.fieldset(
        "contact_information",
        label=_(
            u"label_contact_information",
            default=u"Email Telephone Fax"
        ),
        fields=[
            "email_address",
            "business_phone",
            "business_fax",
            "home_phone",
            "mobile_phone",
        ]
    )

    email_address = schema.TextLine(
        title=_(
            u"label_person_email_address",
            default=u"Email Address"
        ),
        required=False,
    )

    directives.widget("business_phone", PhoneWidget)
    business_phone = PhoneField(
        title=_(
            u"label_person_business_phone",
            default=u"Phone (business)"
        ),
        required=False,
    )

    directives.widget("business_fax", PhoneWidget)
    business_fax = PhoneField(
        title=_(
            u"label_person_business_fax",
            default=u"Fax (business)"
        ),
        required=False,
    )

    directives.widget("home_phone", PhoneWidget)
    home_phone = PhoneField(
        title=_(
            u"label_person_home_phone",
            default=u"Phone (home)"
        ),
        required=False,
    )

    directives.widget("mobile_phone", PhoneWidget)
    mobile_phone = PhoneField(
        title=_(
            u"label_person_mobile_phone",
            default=u"Phone (mobile)"
        ),
        required=False,
    )

    # Address
    model.fieldset(
        "address",
        label=_(
            u"label_address",
            default=u"Address"
        ),
        fields=[
            "physical_address",
            "postal_address",
        ]
    )

    directives.widget("physical_address", AddressWidget)
    physical_address = AddressField(
        address_types=(PHYSICAL_ADDRESS),
        title=_(
            u"label_person_physical_address",
            default=u"Physical address"
        ),
        required=False,
    )

    directives.widget("postal_address", AddressWidget)
    postal_address = AddressField(
        title=_(
            u"label_person_postal_address",
            default=u"Postal address"
        ),
        address_types=(POSTAL_ADDRESS),
        required=False,
    )

    @invariant
    def validate_email_address(data):
        """Checks if email address is valid
        """
        value = data.email_address
        if not value:
            return

        if not mail.is_valid_email_address(value):
            raise Invalid(_(u"Invalid email address"))


@implementer(IPersonSchema)
class Person(Container):
    """Base class for Person-based content types
    """

    security = ClassSecurityInfo()

    def Title(self):
        """Return the contact's Fullname as title
        """
        return safe_unicode(self.getFullname()).encode("utf-8")

    def getPossibleAddresses(self):
        """Return possible address types
        """
        return ["PhysicalAddress", "PostalAddress"]

    @security.protected(permissions.ModifyPortalContent)
    def setFullname(self, value):
        parts = value.split(" ")
        length = len(parts)
        if length == 2:
            self.setFirstname(parts[0])
            self.setSurname(parts[1])
        elif length == 3:
            self.setFirstname(parts[0])
            self.setMiddlename(parts[1])
            self.setSurname(parts[2])
        elif length == 4:
            self.setFirstname(parts[0])
            self.setMiddleinitial(parts[1])
            self.setMiddlename(parts[2])
            self.setSurname(parts[3])
        else:
            self.setSurname(value)

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
                fullname = "%s %s" % (self.getFirstname(), self.getSurname())
        return fullname.strip()

    @security.protected(permissions.View)
    def getSalutation(self):
        accessor = self.accessor("salutation")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setSalutation(self, value):
        mutator = self.mutator("salutation")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    Salutation = property(getSalutation, setSalutation)

    @security.protected(permissions.View)
    def getFirstname(self):
        accessor = self.accessor("firstname")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setFirstname(self, value):
        mutator = self.mutator("firstname")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    Firstname = property(getFirstname, setFirstname)

    @security.protected(permissions.View)
    def getMiddleinitial(self):
        accessor = self.accessor("middleinitial")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setMiddleinitial(self, value):
        mutator = self.mutator("middleinitial")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    Middleinitial = property(getMiddleinitial, setMiddleinitial)

    @security.protected(permissions.View)
    def getMiddlename(self):
        accessor = self.accessor("middlename")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setMiddlename(self, value):
        mutator = self.mutator("middlename")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    Middlename = property(getMiddlename, setMiddlename)

    @security.protected(permissions.View)
    def getSurname(self):
        accessor = self.accessor("surname")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setSurname(self, value):
        mutator = self.mutator("surname")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    Surname = property(getSurname, setSurname)

    # BBB: AT schema field property
    Fullname = property(getFullname, setFullname)

    @security.protected(permissions.View)
    def getUsername(self):
        accessor = self.accessor("username")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setUsername(self, value):
        mutator = self.mutator("username")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    Username = property(getUsername, setUsername)

    @security.protected(permissions.View)
    def getEmailAddress(self):
        accessor = self.accessor("email_address")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setEmailAddress(self, value):
        mutator = self.mutator("email_address")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    EmailAddress = property(getEmailAddress, setEmailAddress)

    @security.protected(permissions.View)
    def getBusinessPhone(self):
        accessor = self.accessor("business_phone")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setBusinessPhone(self, value):
        mutator = self.mutator("business_phone")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    BusinessPhone = property(getBusinessPhone, setBusinessPhone)

    @security.protected(permissions.View)
    def getBusinessFax(self):
        accessor = self.accessor("business_fax")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setBusinessFax(self, value):
        mutator = self.mutator("business_fax")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    BusinessFax = property(getBusinessFax, setBusinessFax)

    @security.protected(permissions.View)
    def getHomePhone(self):
        accessor = self.accessor("home_phone")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setHomePhone(self, value):
        mutator = self.mutator("home_phone")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    HomePhone = property(getHomePhone, setHomePhone)

    @security.protected(permissions.View)
    def getMobilePhone(self):
        accessor = self.accessor("mobile_phone")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setMobilePhone(self, value):
        mutator = self.mutator("mobile_phone")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    MobilePhone = property(getMobilePhone, setMobilePhone)

    @security.protected(permissions.View)
    def getJobTitle(self):
        accessor = self.accessor("job_title")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setJobTitle(self, value):
        mutator = self.mutator("job_title")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    JobTitle = property(getJobTitle, setJobTitle)

    @security.protected(permissions.View)
    def getDepartment(self):
        accessor = self.accessor("department")
        value = accessor(self) or ""
        return safe_unicode(value).encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setDepartment(self, value):
        mutator = self.mutator("department")
        mutator(self, safe_unicode(value))

    # BBB: AT schema field property
    Department = property(getDepartment, setDepartment)

    @security.protected(permissions.View)
    def getPhysicalAddress(self):
        accessor = self.accessor("physical_address")
        value = accessor(self)
        # The address field returns a list of address dicts
        if value and isinstance(value, list):
            value = value[0]
        if not isinstance(value, dict):
            value = self.get_empty_address(PHYSICAL_ADDRESS)
        return value

    @security.protected(permissions.ModifyPortalContent)
    def setPhysicalAddress(self, value):
        mutator = self.mutator("physical_address")
        mutator(self, value)

    # BBB: AT schema field property
    PhysicalAddress = property(getPhysicalAddress, setPhysicalAddress)

    @security.protected(permissions.View)
    def getPostalAddress(self):
        accessor = self.accessor("postal_address")
        value = accessor(self)
        # The address field returns a list of address dicts
        if value and isinstance(value, list):
            value = value[0]
        if not isinstance(value, dict):
            value = self.get_empty_address(POSTAL_ADDRESS)
        return value

    @security.protected(permissions.ModifyPortalContent)
    def setPostalAddress(self, value):
        mutator = self.mutator("postal_address")
        mutator(self, value)

    # BBB: AT schema field property
    PostalAddress = property(getPostalAddress, setPostalAddress)

    # Helper methods for address fields (computed fields in old Person schema)
    def getCity(self):
        """Return city from physical address
        """
        address = self.getPhysicalAddress()
        if not address:
            return ""
        return address.get("city", "")

    def getDistrict(self):
        """Return district from physical address
        """
        address = self.getPhysicalAddress()
        if not address:
            return ""
        return address.get("subdivison2", "")

    def getPostalCode(self):
        """Return postal code from physical address
        """
        address = self.getPhysicalAddress()
        if not address:
            return ""
        return address.get("postalCode", "")

    def getCountry(self):
        """Return country from physical address
        """
        address = self.getPhysicalAddress()
        if not address:
            return ""
        return address.get("country", "")

    @security.protected(permissions.ManagePortal)
    def hasUser(self):
        """Check if person has user
        """
        from plone import api
        return api.user.get(userid=self.getUsername()) is not None

    def get_empty_address(self, address_type):
        """Returns a dict that represents an empty address for the given type
        """
        return {
            "type": address_type,
            "address": "",
            "zip": "",
            "city": "",
            "subdivision2": "",
            "subdivision1": "",
            "country": "",
        }
