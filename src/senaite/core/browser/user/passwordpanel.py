# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from plone.app.users.browser.passwordpanel import PasswordPanel as Base
from plone.app.users.utils import notifyWidgetActionExecutionError
from plone.autoform import directives
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import Interface


class IPasswordSchema(Interface):
    """User Password Schema
    """
    directives.widget("new_password", klass="form-control form-control-sm")
    new_password = schema.Password(
        title=_(u"label_new_password", default=u"New password"),
        description=_(
            u"help_new_password",
            default=u"Enter your new password."),
    )
    directives.widget("new_password_ctl", klass="form-control form-control-sm")
    new_password_ctl = schema.Password(
        title=_(u"label_confirm_password", default=u"Confirm password"),
        description=_(
            u"help_confirm_password",
            default=u"Re-enter the password. "
            u"Make sure the passwords are identical."),
    )


class PasswordPanelAdapter(object):
    """Data manager for Password
    """

    def __init__(self, context):
        self.context = context

    def get_dummy(self):
        """We don't actually need to 'get' anything ...
        """
        return ""

    new_password = property(get_dummy)
    new_password_ctl = property(get_dummy)


class PasswordPanel(Base):
    template = ViewPageTemplateFile("templates/account-panel.pt")
    schema = IPasswordSchema

    def validate_password(self, action, data):
        """Validate new password

        NOTE: We do not check the current password and allow to set a
              new password directly
        """
        registration = api.get_tool("portal_registration")

        # check if passwords are same and valid according to the PAS plugin
        new_password = data.get("new_password")
        new_password_ctl = data.get("new_password_ctl")

        if new_password and new_password_ctl:
            err_str = registration.testPasswordValidity(new_password,
                                                        new_password_ctl)

            if err_str:
                # add error to new_password widget
                notifyWidgetActionExecutionError(action,
                                                 "new_password", err_str)
                notifyWidgetActionExecutionError(action,
                                                 "new_password_ctl", err_str)
