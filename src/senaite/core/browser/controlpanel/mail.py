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

import socket
import smtplib
import sys
from logging import getLogger

import six
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.mail import \
    MailControlPanelForm as BaseMailControlPanelForm
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.MailHost.MailHost import MailHostError
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from senaite.core.i18n import translate as t
from bika.lims import senaiteMessageFactory as _
from z3c.form import button
from zope.component import getUtility

logger = getLogger("senaite.core")

# How long to wait for the mail server to answer. Long enough for a
# server anywhere in the world to accept the connection, short enough
# that a wrong host does not hold the form open.
TEST_MAIL_TIMEOUT = 3

TEST_MAIL_SUBJECT = _(
    "subject_test_email",
    default=u"Test e-mail from SENAITE")

TEST_MAIL_BODY = _(
    "body_test_email",
    default=u"Hello,\n\n"
            u"This is a test message from the mail settings of your "
            u"SENAITE installation.\n\n"
            u"If it reached you, outgoing mail is working, and the "
            u"results reports and notifications your laboratory sends "
            u"will find their recipients too.\n\n"
            u"Nothing else to do here. Have a good day.\n\n"
            u"SENAITE")


class MailControlPanelForm(BaseMailControlPanelForm):
    """Mail settings, with a test message that says who sent it.

    The stock message signs off in the name of the underlying
    framework, which is not what the laboratory installed, and says
    nothing about what the setting is for. It lands in the mailbox of
    whoever is setting the system up, and it is often the first thing
    SENAITE ever sends them.

    Only the handler behind the test button changes. The buttons
    themselves are inherited, and the handlers are copied first so that
    Save and Cancel keep theirs.
    """

    handlers = BaseMailControlPanelForm.handlers.copy()

    def get_from_address(self):
        """Return the address the site sends from, and sends the test to"""
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        return settings.email_from_address

    def get_charset(self):
        """Return the charset configured for outgoing mail"""
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        return settings.email_charset

    def send_test_email(self):
        """Send the test message, returning the error if there was one

        :returns: None when the message went out, the exception otherwise
        """
        mailhost = getToolByName(self.context, "MailHost")
        address = self.get_from_address()
        # Keep the timeout short, and put back whatever it was: it is a
        # process-wide setting and everything else in the instance
        # shares it.
        timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(TEST_MAIL_TIMEOUT)
            mailhost.send(t(TEST_MAIL_BODY),
                          mto=address,
                          mfrom=address,
                          subject=t(TEST_MAIL_SUBJECT),
                          charset=self.get_charset(),
                          immediate=True)
        except (socket.error, MailHostError, smtplib.SMTPException):
            logger.exception("Unable to send test e-mail")
            return sys.exc_info()[1]
        finally:
            socket.setdefaulttimeout(timeout)
        return None

    @button.handler(BaseMailControlPanelForm.buttons["test"])
    def handle_test_action(self, action):
        """Save the settings, then send a test message to the sender"""
        if not self.save():
            return
        error = self.send_test_email()
        if error is None:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Success! Check your mailbox for the test message."),
                type="info")
            return
        IStatusMessage(self.request).addStatusMessage(
            _(u"Unable to send test e-mail ${error}.",
              mapping={"error": six.text_type(error)}),
            type="error")


class MailControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MailControlPanelForm
