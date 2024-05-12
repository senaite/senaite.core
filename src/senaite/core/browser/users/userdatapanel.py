# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IContact
from bika.lims.interfaces import ILabContact
from plone.app.users.browser.account import getSchema
from plone.app.users.browser.userdatapanel import UserDataPanel as Base
from plone.app.users.browser.userdatapanel import UserDataPanelAdapter
from plone.app.users.schema import ProtectedEmail
from plone.app.users.schema import ProtectedTextLine
from plone.app.users.schema import checkEmailAddress
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface


class IUserDataSchema(Interface):
    """Custom User Data Schema
    """

    fullname = ProtectedTextLine(
        title=_(u"label_full_name", default=u"Full Name"),
        description=_(u"help_full_name_creation",
                      default=u"Enter full name, e.g. John Smith."),
        required=False)

    email = ProtectedEmail(
        title=_(u"label_email", default=u"Email"),
        description=u"We will use this address if you need to recover your "
                    u"password",
        required=True,
        constraint=checkEmailAddress,
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
    template = ViewPageTemplateFile("templates/account-panel.pt")

    @property
    def schema(self):
        schema = getUserDataSchema()
        return schema

    def updateWidgets(self):
        super(UserDataPanel, self).updateWidgets()

    def __call__(self):
        userid = self.request.form.get("userid")
        user = api.get_user(userid) or api.get_current_user()
        contact = api.get_user_contact(user)
        if IContact.providedBy(contact):
            self.add_status_message(
                _("User is linked to the client contact '%s' (%s)" %
                  (contact.getFullname(), contact.aq_parent.getName())))
        elif ILabContact.providedBy(contact):
            self.add_status_message(
                _("User is linked to lab contact '%s'" %
                  contact.getFullname()))
        return super(UserDataPanel, self).__call__()

    def add_status_message(self, message, level="info"):
        """Add a portal status message
        """
        plone_utils = api.get_tool("plone_utils")
        return plone_utils.addPortalMessage(message, level)
