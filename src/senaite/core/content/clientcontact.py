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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

import re

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.api.mail import is_valid_email_address
from bika.lims.interfaces import IClient
from bika.lims.interfaces import IDeactivable
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.interfaces import IClientContact
from senaite.core.schema import AddressField
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.schema.addressfield import POSTAL_ADDRESS
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from six import string_types
from zope import schema
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant


def is_valid_phone(phone):
    """Returns whether the given phone is valid or not
    """
    # XXX Better validate with phonenumbers library here?
    # https://pypi.org/project/phonenumbers/
    phone = phone.strip()
    match = re.match(r"^[+(]?\d+(?:[- )(]+\d+)+$", phone)
    if not match:
        return False
    return True


class IClientContactSchema(model.Schema):
    """Client's Contact Schema interface
    """

    salutation = schema.TextLine(
        title=_(u"Salutation"),
        description=_(
            u"Greeting title eg. Mr, Mrs, Dr"
        ),
        required=False,
    )

    firstname = schema.TextLine(
        title=_(u"Firstname"),
        required=True,
    )

    lastname = schema.TextLine(
        title=_(u"Lastname"),
        required=True,
    )

    directives.omitted("username")
    username = schema.TextLine(
        title=_(u"Username"),
        required=False,
    )

    email = schema.TextLine(
        title=_(u"Email"),
        required=False,
    )

    business_phone = schema.TextLine(
        title=_(u"Phone (business)"),
        required=False,
    )

    mobile_phone = schema.TextLine(
        title=_(u"Phone (mobile)"),
        required=False,
    )

    home_phone = schema.TextLine(
        title=_(u"Phone (home)"),
        required=False,
    )

    job_title = schema.TextLine(
        title=_(u"Job title"),
        required=False,
    )

    department = schema.TextLine(
        title=_(u"Department"),
        required=False,
    )

    address = AddressField(
        title=_(u"Address"),
        address_types=[
            PHYSICAL_ADDRESS,
            POSTAL_ADDRESS,
        ]
    )

    cc_contacts = UIDReferenceField(
        title=_(u"Contacts to CC"),
        description=_(
            u"Contacts that will receive a copy of the notification emails "
            u"sent to this contact. Only contacts from same client are allowed"
        ),
        allowed_types=("ClientContact", ),
        multi_valued=True,
        required=False,
    )

    directives.widget(
        "cc_contacts",
        UIDReferenceWidgetFactory,
        catalog="portal_catalog",
        query="get_cc_contacts_query",
        display_template="<a href='${url}'>${title}</a>",
        columns=[
            {
                "name": "title",
                "width": "30",
                "align": "left",
                "label": _(u"Title"),
            }, {
                "name": "description",
                "width": "70",
                "align": "left",
                "label": _(u"Description"),
            },
        ],
        limit=15,

    )

    # Notification preferences fieldset
    model.fieldset(
        "notification_preferences",
        label=_(u"Notification preferences"),
        fields=["cc_contacts",]
    )

    @invariant
    def validate_email(self):
        """Checks if the email is correct
        """
        email = self.email
        if not email:
            return

        email = email.strip()
        if not is_valid_email_address(email):
            raise Invalid(_("Email is not valid"))

    def validate_phone(self, field_name):
        phone = getattr(self, field_name)
        if not phone:
            return

        if not is_valid_phone(phone):
            raise Invalid(_("Phone is not valid"))

    @invariant
    def validate_business_phone(self):
        """Checks if the business phone is correct
        """
        self.validate_phone("business_phone")

    @invariant
    def validate_home_phone(self):
        """Checks if the home phone is correct
        """
        self.validate_phone("home_phone")

    @invariant
    def validate_mobile_phone(self):
        """Checks if the mobile phone is correct
        """
        self.validate_phone("mobile_phone")


@implementer(IClientContact, IClientContactSchema, IDeactivable)
class ClientContact(Container):
    """Client Contact type
    """
    # Catalogs where this type will be catalogued
    _catalogs = ["portal_catalog"]

    security = ClassSecurityInfo()

    @security.private
    def accessor(self, fieldname):
        """Return the field accessor for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        return schema[fieldname].get

    @security.private
    def mutator(self, fieldname):
        """Return the field mutator for the fieldname
        """
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        return schema[fieldname].set

    @security.protected(permissions.View)
    def Title(self):
        return self.getFullname()

    @security.private
    def set_string_value(self, field_name, value, validator=None):
        if not isinstance(value, string_types):
            value = u""

        value = value.strip()
        if validator:
            validator(value)

        mutator = self.mutator(field_name)
        mutator(self, api.safe_unicode(value))

    @security.private
    def get_string_value(self, field_name, default=""):
        accessor = self.accessor(field_name)
        value = accessor(self) or default
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setSalutation(self, value):
        self.set_string_value("salutation", value)

    @security.protected(permissions.View)
    def getSalutation(self):
        return self.get_string_value("salutation")

    @security.protected(permissions.ModifyPortalContent)
    def setFirstname(self, value):
        self.set_string_value("firstname", value)

    @security.protected(permissions.View)
    def getFirstname(self):
        return self.get_string_value("firstname")

    @security.protected(permissions.ModifyPortalContent)
    def setLastname(self, value):
        self.set_string_value("lastname", value)

    @security.protected(permissions.View)
    def getLastname(self):
        return self.get_string_value("lastname")

    @security.protected(permissions.ModifyPortalContent)
    def setEmail(self, value):
        def validate_email(email):
            if email and not is_valid_email_address(email):
                raise ValueError("Email is not valid")

        self.set_string_value("email", value, validator=validate_email)

    @security.protected(permissions.View)
    def getEmail(self):
        return self.get_string_value("email")

    @security.protected(permissions.ModifyPortalContent)
    def setBusinessPhone(self, value):
        def validate_phone(phone):
            if phone and not is_valid_phone(phone):
                raise ValueError("Phone is not valid")

        self.set_string_value("business_phone", value, validator=validate_phone)

    @security.protected(permissions.View)
    def getBusinessPhone(self):
        return self.get_string_value("business_phone")

    @security.protected(permissions.ModifyPortalContent)
    def setMobilePhone(self, value):
        def validate_phone(phone):
            if phone and not is_valid_phone(phone):
                raise ValueError("Phone is not valid")

        self.set_string_value("mobile_phone", value, validator=validate_phone)

    @security.protected(permissions.View)
    def getMobilePhone(self):
        return self.get_string_value("mobile_phone")

    @security.protected(permissions.ModifyPortalContent)
    def setHomePhone(self, value):
        def validate_phone(phone):
            if phone and not is_valid_phone(phone):
                raise ValueError("Phone is not valid")

        self.set_string_value("home_phone", value, validator=validate_phone)

    @security.protected(permissions.View)
    def getHomePhone(self):
        return self.get_string_value("home_phone")

    @security.protected(permissions.ModifyPortalContent)
    def setJobTitle(self, value):
        self.set_string_value("job_title", value)

    @security.protected(permissions.View)
    def getJobTitle(self):
        return self.get_string_value("job_title")

    @security.protected(permissions.ModifyPortalContent)
    def setDepartment(self, value):
        self.set_string_value("department", value)

    @security.protected(permissions.View)
    def getDepartment(self):
        return self.get_string_value("department")

    @security.protected(permissions.ModifyPortalContent)
    def setAddress(self, value):
        mutator = self.mutator("address")
        mutator(self, value)

    @security.protected(permissions.View)
    def getAddress(self):
        accessor = self.accessor("address")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setCCContacts(self, value):
        mutator = self.mutator("cc_contacts")
        mutator(self, value)

    @security.protected(permissions.View)
    def getCCContacts(self, as_objects=False):
        accessor = self.accessor("cc_contacts")
        uids = accessor(self, as_objects=as_objects) or []
        return [uid.encode("utf.8") for uid in uids]

    @security.protected(permissions.View)
    def getFullname(self):
        """Returns the fullname of this Client Contact
        """
        full = filter(None, [self.getFirstname(), self.getLastname()])
        return " ".join(full)

    @security.protected(permissions.View)
    def getClient(self):
        """Returns the client this Client Contact belongs to
        """
        obj = api.get_parent(self)
        if IClient.providedBy(obj):
            return obj
        return None

    @security.private
    def get_cc_contacts_query(self):
        """Returns the default query for the cc_contacts field. Only contacts
        from same client as the current one are displayed, if client set
        """
        query = {
            "portal_type": "ClientContact",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        }
        client = self.getClient()
        if client:
            query.update({
                "path": {
                    "query": api.get_path(client),
                    "level": 0
                }
            })

        return query
