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

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IContact
from bika.lims.interfaces import ILabContact
from bika.lims.utils import get_link_for
from plone.app.users.browser.account import getSchema
from plone.app.users.browser.userdatapanel import UserDataPanel as Base
from plone.app.users.browser.userdatapanel import UserDataPanelAdapter
from plone.app.users.schema import ProtectedEmail
from plone.app.users.schema import ProtectedTextLine
from plone.app.users.schema import checkEmailAddress
from plone.autoform import directives
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.catalog import CONTACT_CATALOG
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import DISPLAY_MODE
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import Interface
from zope.interface import implementer
from zope.schema import TextLine


class ContactLinkWidget(TextWidget):
    """Widget to render contact UID as a clickable link
    """
    def render(self):
        if not self.value:
            return None
        return get_link_for(self.value)


@implementer(IFieldWidget)
def ContactLinkWidgetFactory(field, request):
    return FieldWidget(field, ContactLinkWidget(request))


class IUserDataSchema(Interface):
    """Custom User Data Schema
    """

    fullname = ProtectedTextLine(
        title=_(u"label_user_full_name", default=u"Full Name"),
        description=_(u"help_full_name_creation",
                      default=u"Enter full name, e.g. John Smith."),
        required=False)

    email = ProtectedEmail(
        title=_(u"label_user_email", default=u"Email"),
        description=u"We will use this address if you need to recover your "
                    u"password",
        required=True,
        constraint=checkEmailAddress,
    )

    # Field behaves like a readonly field
    directives.mode(contact=DISPLAY_MODE)
    directives.widget("contact", ContactLinkWidgetFactory)
    contact = TextLine(
        title=_(u"label_user_contact", default=u"Contact"),
        description=_(u"description_user_contact",
                      default=u"User is linked to a contact. "
                      u"Please change your settings in the contact profile."),
        required=False,
    )


def getUserDataSchema():
    form_name = u"In User Profile"
    # This is needed on Plone 6, but has a bad side effect on Plone 5:
    # as Manager you go to a member and then to your own personal-information
    # form and you see the data of the member you just visited.
    # I keep the code here commented out as warning in case someone compares
    # the code.
    # if getSecurityManager().checkPermission('Manage portal', portal):
    #     form_name = None
    schema = getSchema(
        IUserDataSchema, UserDataPanelAdapter, form_name=form_name)
    return schema


class UserDataPanel(Base):
    """Provides user properties in the profile
    """
    template = ViewPageTemplateFile("templates/account-panel.pt")

    def __init__(self, context, request):
        super(UserDataPanel, self).__init__(context, request)

    def __call__(self):
        submitted = self.request.form.get("Save", False)
        if not submitted:
            self.notify_linked_user()
        return super(UserDataPanel, self).__call__()

    def _on_save(self, data=None):
        contact = api.get_user_contact(self.member)
        if not contact:
            return
        # update the fullname
        fullname = data.get("fullname")
        if fullname:
            contact.setFullname(fullname)
        # update the email
        email = data.get("email")
        if email:
            contact.setEmailAddress(email)

    @property
    def label(self):
        fullname = self.member.getProperty("fullname")
        username = self.member.getUserName()
        if fullname:
            # username/fullname are already encoded in UTF8
            return "%s (%s)" % (fullname, username)
        return username

    @property
    def schema(self):
        schema = getUserDataSchema()
        return schema

    def updateWidgets(self, prefix=None):
        super(UserDataPanel, self).updateWidgets(prefix=prefix)
        # check if we are linked to a contact
        contact = self.get_linked_contact()
        if not contact:
            # remove the widget and return
            return self.remove_widgets("contact")
        # update the contact widget and remove the email/fullname widgets
        widget = self.widgets.get("contact")
        if widget:
            widget.value = api.safe_unicode(api.get_uid(contact))
            # remove the email/fullname widgets
            self.remove_widgets("email", "fullname")

    def remove_widgets(self, *names):
        """Removes the widgets from the form
        """
        for name in names:
            widget = self.widgets.get(name)
            if not widget:
                continue
            del self.widgets[name]

    def get_linked_contact(self):
        """Returns the linked contact object
        """
        query = {"getUsername": self.member.getId()}
        brains = api.search(query, CONTACT_CATALOG)
        if len(brains) == 0:
            return None
        return api.get_object(brains[0])

    def notify_linked_user(self):
        """Add notification message if user is linked to a contact
        """
        contact = self.get_linked_contact()
        if ILabContact.providedBy(contact):
            self.add_status_message(_(
                "User is linked to lab contact '${fullname}'",
                mapping={"fullname": api.safe_unicode(contact.getFullname())}
            ))

        elif IContact.providedBy(contact):
            fullname = contact.getFullname()
            client_name = contact.aq_parent.getName()
            self.add_status_message(_(
                "User is linked to the client contact '${fullname}' "
                "(${client_name})",
                mapping={
                    "fullname": api.safe_unicode(fullname),
                    "client_name": api.safe_unicode(client_name)
                }
            ))

    def add_status_message(self, message, level="info"):
        """Add a portal status message
        """
        plone_utils = api.get_tool("plone_utils")
        return plone_utils.addPortalMessage(message, level)


class UserDataConfiglet(UserDataPanel):
    """Control panel version of the userdata panel
    """
    template = ViewPageTemplateFile("templates/account-configlet.pt")
